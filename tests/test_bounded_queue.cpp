#include "edge_ai_defect/runtime/bounded_queue.hpp"

#include <atomic>
#include <chrono>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace {
using edge_ai_defect::runtime::BoundedQueue;
using edge_ai_defect::runtime::FirstErrorCancellation;
using edge_ai_defect::runtime::QueuePopStatus;
using edge_ai_defect::runtime::QueuePushResult;
using namespace std::chrono_literals;

void require(bool value, const char* message) {
    if (!value) throw std::runtime_error(message);
}

void fifo_and_capacity() {
    bool rejected_zero_capacity = false;
    try { BoundedQueue<int> invalid(0); } catch (const std::invalid_argument&) { rejected_zero_capacity = true; }
    require(rejected_zero_capacity, "zero capacity accepted");

    for (const std::size_t capacity : {1U, 4U}) {
        BoundedQueue<int> queue(capacity);
        std::thread producer([&] {
            for (int i = 0; i < 20; ++i) require(queue.push(i) == QueuePushResult::PUSHED, "push");
            queue.close();
        });
        for (int i = 0; i < 20; ++i) {
            auto result = queue.pop();
            require(result.status == QueuePopStatus::ITEM && result.item->value == i, "FIFO");
            require(result.item->enqueued_ns != 0, "timestamp missing");
        }
        producer.join();
        const auto stats = queue.statistics();
        require(stats.high_water_mark <= capacity, "high water exceeded capacity");
        require(stats.push_count == 20 && stats.residence_count == 20, "statistics count");
        require(queue.pop().status == QueuePopStatus::EOS, "FIFO EOS");
    }
}

void blocking_and_close() {
    BoundedQueue<int> queue(1);
    queue.push(1);
    std::atomic<bool> started{false};
    std::atomic<bool> pushed{false};
    std::thread producer([&] {
        started = true;
        pushed = queue.push(2) == QueuePushResult::PUSHED;
    });
    while (!started.load()) std::this_thread::yield();
    std::this_thread::sleep_for(10ms);
    require(!pushed.load(), "full queue did not block");
    require(queue.pop().item->value == 1, "release pop");
    producer.join();
    require(pushed.load(), "blocked producer did not recover");
    require(queue.statistics().push_block_total_ns > 0, "push blocking was not measured");
    queue.close(); queue.close();
    require(queue.push(3) == QueuePushResult::CLOSED, "closed accepted push");
    require(queue.pop().item->value == 2, "closed did not drain");
    require(queue.pop().status == QueuePopStatus::EOS, "closed did not return EOS");
}

void consumer_wait_and_cancel() {
    BoundedQueue<int> queue(2);
    std::atomic<bool> waiting{false};
    QueuePopStatus status = QueuePopStatus::ITEM;
    std::thread consumer([&] { waiting = true; status = queue.pop().status; });
    while (!waiting.load()) std::this_thread::yield();
    std::this_thread::sleep_for(10ms);
    queue.push(7);
    consumer.join();
    require(status == QueuePopStatus::ITEM, "consumer did not recover after push");

    BoundedQueue<int> waiting_queue(1);
    std::atomic<bool> cancelled_consumer{false};
    std::thread cancelled_reader([&] {
        cancelled_consumer = waiting_queue.pop().status == QueuePopStatus::CANCELLED;
    });
    std::this_thread::sleep_for(10ms);
    waiting_queue.cancel();
    cancelled_reader.join();
    require(cancelled_consumer.load(), "cancel did not wake consumer");

    BoundedQueue<int> blocked_queue(1);
    blocked_queue.push(1);
    std::atomic<bool> cancelled_producer{false};
    std::thread blocked_writer([&] {
        cancelled_producer = blocked_queue.push(2) == QueuePushResult::CANCELLED;
    });
    std::this_thread::sleep_for(10ms);
    blocked_queue.cancel();
    blocked_writer.join();
    require(cancelled_producer.load(), "cancel did not wake producer");

    queue.push(8); queue.push(9); queue.cancel(); queue.cancel();
    require(queue.state() == edge_ai_defect::runtime::QueueState::CANCELLED, "cancel state");
    require(queue.pop().status == QueuePopStatus::CANCELLED, "cancel did not clear");
    require(queue.push(10) == QueuePushResult::CANCELLED, "cancel accepted push");

    BoundedQueue<int> transition(1);
    transition.push(1); transition.close(); transition.cancel();
    require(transition.pop().status == QueuePopStatus::CANCELLED, "cancel did not dominate close");
}

void cancellation_primitive() {
    FirstErrorCancellation cancellation;
    require(cancellation.cancel_with_error("first"), "first cancellation");
    require(!cancellation.cancel_with_error("second") && !cancellation.cancel(), "cancel not idempotent");
    require(cancellation.cancelled() && cancellation.first_error() == std::optional<std::string>("first"), "first error overwritten");
}

void stress() {
    constexpr int rounds = 30;
    constexpr int count = 300;
    for (int round = 0; round < rounds; ++round) {
        BoundedQueue<int> queue(3);
        std::thread producer([&] { for (int i = 0; i < count; ++i) require(queue.push(i) == QueuePushResult::PUSHED, "stress push"); queue.close(); });
        std::thread consumer([&] { for (int i = 0; i < count; ++i) { auto item = queue.pop(); require(item.status == QueuePopStatus::ITEM && item.item->value == i, "stress FIFO"); } require(queue.pop().status == QueuePopStatus::EOS, "stress EOS"); });
        producer.join(); consumer.join();
        require(queue.statistics().high_water_mark <= 3, "stress high water");
    }
}
}  // namespace

int main() {
    try {
        fifo_and_capacity(); blocking_and_close(); consumer_wait_and_cancel(); cancellation_primitive(); stress();
        std::cout << "BoundedQueue tests passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "BoundedQueue test failed: " << error.what() << '\n';
        return 1;
    }
}
