#pragma once

#include "edge_ai_defect/runtime/result_sink.hpp"

#include <cstddef>
#include <filesystem>
#include <memory>
#include <vector>

namespace edge_ai_defect::runtime {

class JsonSink final : public IResultSink {
public:
    [[nodiscard]] static core::Status create(
        const std::filesystem::path& target_path,
        bool overwrite,
        std::unique_ptr<JsonSink>* output);

    ~JsonSink() override;

    [[nodiscard]] core::Status begin_run(const RunMetadata& metadata) override;
    [[nodiscard]] core::Status write_frame(const FrameResult& frame) override;
    [[nodiscard]] core::Status end_run(const RunSummary& summary) override;

private:
    enum class State { kReady, kActive, kCompleted, kFailed };

    JsonSink(std::filesystem::path target_path, bool overwrite);
    void remove_temporary_file() noexcept;

    std::filesystem::path target_path_;
    std::filesystem::path temporary_path_;
    bool overwrite_ = false;
    State state_ = State::kReady;
    RunMetadata metadata_;
    std::vector<FrameResult> frames_;
    std::size_t received_detections_ = 0;
};

}  // namespace edge_ai_defect::runtime
