#pragma once

#include <chrono>
#include <condition_variable>
#include <cstddef>
#include <cstdint>
#include <deque>
#include <mutex>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>

namespace edge_ai_defect::runtime {

enum class QueueState { OPEN, CLOSED, CANCELLED };

enum class QueuePushResult { PUSHED, CLOSED, CANCELLED };

enum class QueuePopStatus { ITEM, EOS, CANCELLED };

template <typename T>
struct DequeuedItem {
    T value;
    std::uint64_t enqueued_ns = 0;
};

struct BoundedQueueStatistics {
    std::size_t high_water_mark = 0;
    std::uint64_t push_count = 0;
    std::uint64_t residence_count = 0;
    std::uint64_t residence_total_ns = 0;
    std::uint64_t residence_max_ns = 0;
    std::uint64_t push_block_total_ns = 0;
};

template <typename T>
struct QueuePopResult {
    QueuePopStatus status = QueuePopStatus::EOS;
    std::optional<DequeuedItem<T>> item;

    [[nodiscard]] bool has_value() const noexcept {
        return status == QueuePopStatus::ITEM && item.has_value();
    }
};

class FirstErrorCancellation final {
public:
    [[nodiscard]] bool cancel() noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        if (cancelled_) {
            return false;
        }
        cancelled_ = true;
        return true;
    }

    [[nodiscard]] bool cancel_with_error(std::string error) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (cancelled_) {
            return false;
        }
        cancelled_ = true;
        first_error_ = std::move(error);
        return true;
    }

    [[nodiscard]] bool cancelled() const noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        return cancelled_;
    }

    [[nodiscard]] std::optional<std::string> first_error() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return first_error_;
    }

private:
    mutable std::mutex mutex_;
    bool cancelled_ = false;
    std::optional<std::string> first_error_;
};

template <typename T>
class BoundedQueue final {
public:
    explicit BoundedQueue(std::size_t capacity) : capacity_(capacity) {
        if (capacity_ == 0) {
            throw std::invalid_argument("BoundedQueue capacity must be positive");
        }
    }

    BoundedQueue(const BoundedQueue&) = delete;
    BoundedQueue& operator=(const BoundedQueue&) = delete;

    [[nodiscard]] std::size_t capacity() const noexcept { return capacity_; }

    [[nodiscard]] QueueState state() const noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        return state_;
    }

    QueuePushResult push(T value) {
        const auto wait_begin = Clock::now();
        std::unique_lock<std::mutex> lock(mutex_);
        const bool was_full = queue_.size() >= capacity_ && state_ == QueueState::OPEN;
        not_full_.wait(lock, [this] { return queue_.size() < capacity_ || state_ != QueueState::OPEN; });
        if (was_full) {
            push_block_total_ns_ += elapsed_ns(wait_begin, Clock::now());
        }
        if (state_ == QueueState::CANCELLED) {
            return QueuePushResult::CANCELLED;
        }
        if (state_ == QueueState::CLOSED) {
            return QueuePushResult::CLOSED;
        }

        queue_.push_back(Entry{std::move(value), now_ns()});
        ++push_count_;
        if (queue_.size() > high_water_mark_) {
            high_water_mark_ = queue_.size();
        }
        lock.unlock();
        not_empty_.notify_one();
        return QueuePushResult::PUSHED;
    }

    [[nodiscard]] QueuePopResult<T> pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        not_empty_.wait(lock, [this] { return !queue_.empty() || state_ != QueueState::OPEN; });
        if (state_ == QueueState::CANCELLED) {
            return {QueuePopStatus::CANCELLED, std::nullopt};
        }
        if (queue_.empty()) {
            return {QueuePopStatus::EOS, std::nullopt};
        }

        Entry entry = std::move(queue_.front());
        queue_.pop_front();
        const std::uint64_t residence = elapsed_ns(entry.enqueued_ns, now_ns());
        ++residence_count_;
        residence_total_ns_ += residence;
        if (residence > residence_max_ns_) {
            residence_max_ns_ = residence;
        }
        lock.unlock();
        not_full_.notify_one();
        return {QueuePopStatus::ITEM, DequeuedItem<T>{std::move(entry.value), entry.enqueued_ns}};
    }

    void close() noexcept {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (state_ == QueueState::OPEN) {
                state_ = QueueState::CLOSED;
            }
        }
        notify_all();
    }

    void cancel() noexcept {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            state_ = QueueState::CANCELLED;
            queue_.clear();
        }
        notify_all();
    }

    [[nodiscard]] BoundedQueueStatistics statistics() const noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        return {high_water_mark_, push_count_, residence_count_, residence_total_ns_,
                residence_max_ns_, push_block_total_ns_};
    }

private:
    using Clock = std::chrono::steady_clock;
    struct Entry {
        T value;
        std::uint64_t enqueued_ns;
    };

    static std::uint64_t now_ns() noexcept {
        return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(
            Clock::now().time_since_epoch()).count());
    }

    static std::uint64_t elapsed_ns(Clock::time_point begin, Clock::time_point end) noexcept {
        return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin).count());
    }

    static std::uint64_t elapsed_ns(std::uint64_t begin, std::uint64_t end) noexcept {
        return end >= begin ? end - begin : 0;
    }

    void notify_all() noexcept {
        not_full_.notify_all();
        not_empty_.notify_all();
    }

    const std::size_t capacity_;
    mutable std::mutex mutex_;
    std::condition_variable not_full_;
    std::condition_variable not_empty_;
    std::deque<Entry> queue_;
    QueueState state_ = QueueState::OPEN;
    std::size_t high_water_mark_ = 0;
    std::uint64_t push_count_ = 0;
    std::uint64_t residence_count_ = 0;
    std::uint64_t residence_total_ns_ = 0;
    std::uint64_t residence_max_ns_ = 0;
    std::uint64_t push_block_total_ns_ = 0;
};

}  // namespace edge_ai_defect::runtime
