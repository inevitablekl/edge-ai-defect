#include "edge_ai_defect/runtime/composite_sink.hpp"
#include "edge_ai_defect/runtime/console_sink.hpp"
#include "edge_ai_defect/runtime/json_sink.hpp"

#include <cmath>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace {

namespace core = edge_ai_defect::core;
namespace runtime = edge_ai_defect::runtime;
namespace fs = std::filesystem;

class TestContext {
public:
    void expect(bool condition, const std::string& name, const std::string& detail) {
        if (!condition) {
            ++failures_;
            std::cerr << "FAILED: " << name << ": " << detail << '\n';
        }
    }
    [[nodiscard]] int failures() const noexcept { return failures_; }
private:
    int failures_ = 0;
};

runtime::RunMetadata metadata(bool timing_enabled = false) {
    runtime::RunMetadata value;
    value.schema_version = 1;
    value.backend_type = "onnxruntime_cpu";
    value.model_filename = "frozen.onnx";
    value.model_sha256 = std::string(64, 'a');
    value.contract_filename = "frozen.yaml";
    value.class_names = {"crazing", "中文"};
    value.timing_enabled = timing_enabled;
    return value;
}

runtime::FrameResult frame(std::size_t index = 0, bool timing_enabled = false) {
    runtime::FrameResult value;
    value.sequence_index = index;
    value.relative_path = index == 0 ? "a.jpg" : "b.png";
    value.image_width = 200;
    value.image_height = 100;
    value.detections = {
        {1.0F, 2.0F, 20.0F, 30.0F, 0.91F, 1, 123},
        {3.0F, 4.0F, 40.0F, 50.0F, 0.5F, 0, 7},
    };
    if (timing_enabled) {
        value.timings = runtime::FrameTimings{0.1, 1.2, 15.0, 0.4,
                                               16.800000000000001};
    }
    return value;
}

runtime::RunSummary summary(std::size_t images = 1, std::size_t detections = 2) {
    return {images, detections};
}

bool write_text(const fs::path& path, const std::string& value) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    output << value;
    output.close();
    return output.good();
}

std::string read_text(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    return {std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>()};
}

bool no_temporary_files(const fs::path& directory) {
    std::error_code error;
    for (fs::directory_iterator iterator(directory, error), end;
         !error && iterator != end; iterator.increment(error)) {
        if (iterator->path().filename().string().find(".tmp.") != std::string::npos) {
            return false;
        }
    }
    return !error;
}

void test_console(TestContext& context) {
    std::ostringstream output;
    runtime::ConsoleSink sink(output);
    context.expect(!sink.write_frame(frame()).ok(), "console write before begin", "must fail");
    context.expect(!sink.end_run(summary()).ok(), "console end before begin", "must fail");
    const auto run_metadata = metadata();
    context.expect(sink.begin_run(run_metadata).ok(), "console begin", "must succeed");
    context.expect(!sink.begin_run(run_metadata).ok(), "console duplicate begin", "must fail");
    context.expect(sink.write_frame(frame()).ok(), "console write", "must succeed");
    context.expect(sink.end_run(summary()).ok(), "console end", "must succeed");
    context.expect(!sink.write_frame(frame(1)).ok(), "console write after end", "must fail");
    context.expect(!sink.end_run(summary()).ok(), "console duplicate end", "must fail");
    const std::string text = output.str();
    context.expect(text.find("RUN backend=onnxruntime_cpu model=frozen.onnx\n") == 0,
                   "console field order", "RUN line missing");
    context.expect(text.find("IMAGE index=0 path=a.jpg width=200 height=100 detections=2\n") != std::string::npos,
                   "console image", "IMAGE fields missing");
    context.expect(text.find("candidate_index=123\nDETECTION class_id=0") != std::string::npos,
                   "console detection order", "Detection order changed");
    context.expect(text.find("SUMMARY processed_images=1 total_detections=2\n") != std::string::npos,
                   "console summary", "SUMMARY missing");
    context.expect(text.find("source_ms=") == std::string::npos,
                   "console timing disabled", "timing fields must be absent");

    std::ostringstream timing_output;
    runtime::ConsoleSink timing_sink(timing_output);
    context.expect(timing_sink.begin_run(metadata(true)).ok(), "console timing begin", "must succeed");
    context.expect(timing_sink.write_frame(frame(0, true)).ok(), "console timing write", "must succeed");
    context.expect(timing_sink.end_run(summary()).ok(), "console timing end", "must succeed");
    context.expect(timing_output.str().find("source_ms=") != std::string::npos &&
                       timing_output.str().find("pre_sink_total_ms=") != std::string::npos,
                   "console timing enabled", "timing fields missing");

    std::ostringstream invalid_output;
    runtime::ConsoleSink invalid_sink(invalid_output);
    context.expect(invalid_sink.begin_run(metadata()).ok(), "console invalid begin", "must succeed");
    runtime::FrameResult invalid = frame();
    invalid.detections[0].confidence = std::numeric_limits<float>::quiet_NaN();
    context.expect(!invalid_sink.write_frame(invalid).ok(), "console nonfinite", "must reject NaN");
    context.expect(invalid_sink.write_frame(frame()).ok(), "console failed write atomic", "valid retry must succeed");
}

void test_json(TestContext& context, const fs::path& root) {
    const fs::path missing_parent = root / "missing" / "run.json";
    std::unique_ptr<runtime::JsonSink> output;
    context.expect(!runtime::JsonSink::create(missing_parent, false, &output).ok(),
                   "json missing parent", "must fail");

    const fs::path target = root / "result.json";
    const core::Status create_status = runtime::JsonSink::create(target, false, &output);
    context.expect(create_status.ok(), "json create", create_status.message());
    if (!create_status.ok()) return;
    runtime::RunMetadata run_metadata = metadata();
    run_metadata.class_names[1] = "中文";
    context.expect(output->begin_run(run_metadata).ok(), "json begin", "must succeed");
    runtime::FrameResult escaped = frame();
    escaped.relative_path = "quote\" slash\\ control\n.png";
    context.expect(output->write_frame(escaped).ok(), "json write", "must succeed");
    context.expect(!fs::exists(target), "json unpublished before end", "target must not exist");
    context.expect(output->end_run(summary()).ok(), "json end", "must succeed");
    const std::string text = read_text(target);
    context.expect(text.find("  \"schema_version\": 1,\n  \"backend\":") != std::string::npos,
                   "json field order", "top-level order changed");
    context.expect(text.find("\"relative_path\": \"quote\\\" slash\\\\ control\\n.png\"") != std::string::npos,
                   "json escape quote slash control", "escaped path missing");
    context.expect(text.find("中文") != std::string::npos, "json UTF-8", "non-ASCII must remain UTF-8");
    context.expect(text.find("\"timing_ms\"") == std::string::npos,
                   "json timing disabled", "timing_ms must be omitted");
    context.expect(!text.empty() && text.back() == '\n' &&
                       (text.size() == 1U || text[text.size() - 2U] != '\n'),
                   "json final LF", "must end with exactly one LF");
    context.expect(text.find("\"candidate_index\": 123") < text.find("\"candidate_index\": 7"),
                   "json detection order", "Detection order changed");
    context.expect(no_temporary_files(root), "json temporary cleanup", "temporary file leaked");

    std::unique_ptr<runtime::JsonSink> existing;
    context.expect(!runtime::JsonSink::create(target, false, &existing).ok(),
                   "json overwrite false", "existing target must reject");
    context.expect(write_text(target, "old\n"), "json old target setup", "could not write old target");
    std::unique_ptr<runtime::JsonSink> replacing;
    context.expect(runtime::JsonSink::create(target, true, &replacing).ok(), "json overwrite create", "must succeed");
    context.expect(replacing->begin_run(metadata(true)).ok(), "json overwrite begin", "must succeed");
    context.expect(replacing->write_frame(frame(0, true)).ok(), "json overwrite write", "must succeed");
    context.expect(read_text(target) == "old\n", "json old preserved until commit", "old target changed early");
    context.expect(replacing->end_run(summary()).ok(), "json overwrite end", "must succeed");
    context.expect(read_text(target).find("\"timing_ms\"") != std::string::npos,
                   "json timing enabled", "timing_ms missing");

    const fs::path failed_target = root / "failed.json";
    std::unique_ptr<runtime::JsonSink> failed;
    context.expect(runtime::JsonSink::create(failed_target, true, &failed).ok(), "json failure create", "must succeed");
    context.expect(failed->begin_run(metadata()).ok(), "json failure begin", "must succeed");
    runtime::FrameResult bad_sequence = frame(1);
    context.expect(!failed->write_frame(bad_sequence).ok(), "json sequence validation", "must fail");
    runtime::FrameResult absolute_path = frame();
    absolute_path.relative_path = "/absolute.jpg";
    context.expect(!failed->write_frame(absolute_path).ok(), "json absolute path", "must fail");
    runtime::FrameResult nonfinite = frame();
    nonfinite.detections[0].x1 = std::numeric_limits<float>::infinity();
    context.expect(!failed->write_frame(nonfinite).ok(), "json nonfinite", "must fail");
    context.expect(failed->write_frame(frame()).ok(), "json failure atomic", "valid frame must still succeed");
    context.expect(!failed->end_run(summary(2, 2)).ok(), "json summary mismatch", "must fail");
    context.expect(!fs::exists(failed_target), "json failure no target", "target must remain absent");
    context.expect(no_temporary_files(root), "json failure temp cleanup", "temporary file leaked");

    const fs::path preserved_target = root / "preserved.json";
    context.expect(write_text(preserved_target, "old-content\n"), "json preserve setup", "could not write old target");
    std::unique_ptr<runtime::JsonSink> preserving;
    context.expect(runtime::JsonSink::create(preserved_target, true, &preserving).ok(), "json preserve create", "must succeed");
    context.expect(preserving->begin_run(metadata()).ok() && preserving->write_frame(frame()).ok(),
                   "json preserve run", "must succeed before invalid summary");
    context.expect(!preserving->end_run(summary(2, 2)).ok(), "json overwrite failure", "must reject invalid summary");
    context.expect(read_text(preserved_target) == "old-content\n", "json overwrite failure preserves old", "old target changed");

    const fs::path raced_target = root / "raced.json";
    std::unique_ptr<runtime::JsonSink> raced;
    context.expect(runtime::JsonSink::create(raced_target, false, &raced).ok(), "json race create", "must succeed");
    context.expect(raced->begin_run(metadata()).ok() && raced->write_frame(frame()).ok(),
                   "json race run", "must succeed before target appears");
    context.expect(write_text(raced_target, "late-target\n"), "json race target setup", "could not create target");
    context.expect(!raced->end_run(summary()).ok(), "json late target failure", "must not overwrite late target");
    context.expect(read_text(raced_target) == "late-target\n" && no_temporary_files(root),
                   "json late target cleanup", "target changed or temporary leaked");

    const fs::path abandoned = root / "abandoned.json";
    {
        std::unique_ptr<runtime::JsonSink> sink;
        context.expect(runtime::JsonSink::create(abandoned, true, &sink).ok(), "json destructor create", "must succeed");
        context.expect(sink->begin_run(metadata()).ok(), "json destructor begin", "must succeed");
        context.expect(sink->write_frame(frame()).ok(), "json destructor write", "must succeed");
    }
    context.expect(!fs::exists(abandoned) && no_temporary_files(root),
                   "json destructor cleanup", "uncommitted output must not leak");
}

class RecordingSink final : public runtime::IResultSink {
public:
    RecordingSink(std::string name, std::vector<std::string>* calls,
                  std::string fail_operation = {})
        : name_(std::move(name)), calls_(calls), fail_operation_(std::move(fail_operation)) {}
    core::Status begin_run(const runtime::RunMetadata&) override { return call("begin"); }
    core::Status write_frame(const runtime::FrameResult&) override { return call("write"); }
    core::Status end_run(const runtime::RunSummary&) override { return call("end"); }
private:
    core::Status call(const std::string& operation) {
        calls_->push_back(operation + ":" + name_);
        if (operation == fail_operation_) {
            return core::Status::failure(core::ErrorCode::kIoError, "injected failure");
        }
        return core::Status::success();
    }
    std::string name_;
    std::vector<std::string>* calls_;
    std::string fail_operation_;
};

void test_composite(TestContext& context, const fs::path& root) {
    std::vector<std::string> calls;
    std::vector<std::unique_ptr<runtime::IResultSink>> children;
    children.push_back(std::make_unique<RecordingSink>("json", &calls));
    children.push_back(std::make_unique<RecordingSink>("console", &calls));
    std::unique_ptr<runtime::CompositeSink> composite;
    context.expect(runtime::CompositeSink::create(std::move(children), &composite).ok(),
                   "composite create", "must succeed");
    context.expect(composite->begin_run(metadata()).ok(), "composite begin", "must succeed");
    context.expect(composite->write_frame(frame()).ok(), "composite write", "must succeed");
    context.expect(composite->end_run(summary()).ok(), "composite end", "must succeed");
    const std::vector<std::string> expected{
        "begin:json", "begin:console", "write:json", "write:console", "end:console", "end:json"};
    context.expect(calls == expected, "composite order", "begin/write/end order is wrong");

    std::vector<std::unique_ptr<runtime::IResultSink>> null_children(1);
    std::unique_ptr<runtime::CompositeSink> null_composite;
    context.expect(!runtime::CompositeSink::create(std::move(null_children), &null_composite).ok(),
                   "composite null child", "must fail");
    std::vector<std::unique_ptr<runtime::IResultSink>> empty_children;
    context.expect(!runtime::CompositeSink::create(std::move(empty_children), &null_composite).ok(),
                   "composite empty", "must fail");

    calls.clear();
    std::vector<std::unique_ptr<runtime::IResultSink>> failing_children;
    failing_children.push_back(std::make_unique<RecordingSink>("first", &calls));
    failing_children.push_back(std::make_unique<RecordingSink>("middle", &calls, "write"));
    failing_children.push_back(std::make_unique<RecordingSink>("last", &calls));
    std::unique_ptr<runtime::CompositeSink> failing;
    context.expect(runtime::CompositeSink::create(std::move(failing_children), &failing).ok(), "composite failure create", "must succeed");
    context.expect(failing->begin_run(metadata()).ok(), "composite failure begin", "must succeed");
    context.expect(!failing->write_frame(frame()).ok(), "composite middle write failure", "must fail");
    context.expect(calls == std::vector<std::string>{"begin:first", "begin:middle", "begin:last", "write:first", "write:middle"},
                   "composite failure stop", "later child must not be called");

    calls.clear();
    std::vector<std::unique_ptr<runtime::IResultSink>> begin_failing_children;
    begin_failing_children.push_back(std::make_unique<RecordingSink>("first", &calls));
    begin_failing_children.push_back(std::make_unique<RecordingSink>("middle", &calls, "begin"));
    begin_failing_children.push_back(std::make_unique<RecordingSink>("last", &calls));
    std::unique_ptr<runtime::CompositeSink> begin_failing;
    context.expect(runtime::CompositeSink::create(std::move(begin_failing_children), &begin_failing).ok(), "composite begin failure create", "must succeed");
    context.expect(!begin_failing->begin_run(metadata()).ok(), "composite middle begin failure", "must fail");
    context.expect(calls == std::vector<std::string>{"begin:first", "begin:middle"},
                   "composite begin failure stop", "later child must not be called");

    calls.clear();
    std::vector<std::unique_ptr<runtime::IResultSink>> end_failing_children;
    end_failing_children.push_back(std::make_unique<RecordingSink>("json", &calls));
    end_failing_children.push_back(std::make_unique<RecordingSink>("middle", &calls, "end"));
    end_failing_children.push_back(std::make_unique<RecordingSink>("last", &calls));
    std::unique_ptr<runtime::CompositeSink> end_failing;
    context.expect(runtime::CompositeSink::create(std::move(end_failing_children), &end_failing).ok(), "composite end failure create", "must succeed");
    context.expect(end_failing->begin_run(metadata()).ok() && end_failing->write_frame(frame()).ok(),
                   "composite end failure run", "must succeed before end");
    context.expect(!end_failing->end_run(summary()).ok(), "composite middle end failure", "must fail");
    context.expect(calls == std::vector<std::string>{"begin:json", "begin:middle", "begin:last", "write:json", "write:middle", "write:last", "end:last", "end:middle"},
                   "composite end failure stop", "earlier child must not be called after failure");

    const fs::path target = root / "composite.json";
    std::unique_ptr<runtime::JsonSink> json;
    const core::Status json_create = runtime::JsonSink::create(target, true, &json);
    context.expect(json_create.ok(), "composite json create", json_create.message());
    if (!json_create.ok()) {
        return;
    }
    calls.clear();
    std::vector<std::unique_ptr<runtime::IResultSink>> guarded_children;
    guarded_children.push_back(std::move(json));
    guarded_children.push_back(std::make_unique<RecordingSink>("console", &calls, "end"));
    std::unique_ptr<runtime::CompositeSink> guarded;
    context.expect(runtime::CompositeSink::create(std::move(guarded_children), &guarded).ok(), "composite guarded create", "must succeed");
    context.expect(guarded->begin_run(metadata()).ok() && guarded->write_frame(frame()).ok(),
                   "composite guarded run", "must succeed");
    context.expect(!guarded->end_run(summary()).ok(), "composite console end failure", "must fail");
    context.expect(!fs::exists(target), "composite json commit guard", "JsonSink must not commit");
}

}  // namespace

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: test_result_sinks <temp-dir>\n";
        return 2;
    }
    const fs::path root = fs::path(argv[1]) / "result_sinks_cases";
    std::error_code error;
    fs::remove_all(root, error);
    fs::create_directories(root, error);
    if (error) {
        std::cerr << "Could not prepare test directory: " << error.message() << '\n';
        return 2;
    }
    TestContext context;
    test_console(context);
    test_json(context, root);
    test_composite(context, root);
    fs::remove_all(root, error);
    context.expect(!error, "test cleanup", error.message());
    if (context.failures() != 0) {
        std::cerr << context.failures() << " ResultSink test(s) failed\n";
        return 1;
    }
    std::cout << "All ResultSink tests passed\n";
    return 0;
}
