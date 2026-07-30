#include "edge_ai_defect/runtime/frame_trace.hpp"

#include <iostream>
#include <sstream>
#include <string>

namespace {

int failures = 0;

void expect(bool condition, const std::string& name, const std::string& detail = {}) {
    if (!condition) {
        ++failures;
        std::cerr << "FAILED: " << name;
        if (!detail.empty()) std::cerr << ": " << detail;
        std::cerr << '\n';
    }
}

using namespace edge_ai_defect::runtime;

// ============================================================================
// Old TraceRecorder regression
// ============================================================================
void test_trace_recorder_regression() {
    std::ostringstream output;
    TraceRecorder recorder(output, false);

    // First begin succeeds
    expect(recorder.on_stage_begin(0, FrameTraceStage::kSource, 100).ok(), "TR begin ok", "must succeed");
    // Non-monotonic timestamp rejected
    expect(!recorder.on_stage_begin(1, FrameTraceStage::kInference, 50).ok(),
           "TR non-monotonic begin", "must reject");
    // Missing matching end (wrong stage)
    expect(!recorder.on_stage_end(0, FrameTraceStage::kInference, 200).ok(),
           "TR end mismatch stage", "must reject wrong stage");
    // Active stage end with wrong cycle_id
    expect(!recorder.on_stage_end(1, FrameTraceStage::kSource, 200).ok(),
           "TR end wrong cycle", "must reject wrong cycle_id");

    // Valid end
    expect(recorder.on_stage_end(0, FrameTraceStage::kSource, 200).ok(),
           "TR valid end", "must succeed");
    expect(output.str().find("\"cycle_id\":0") != std::string::npos, "TR output cycle", "output missing cycle");
    expect(output.str().find("\"duration_ns\":100") != std::string::npos, "TR output duration", "duration mismatch");
    expect(recorder.flush().ok(), "TR flush", "must succeed");
}

// ============================================================================
// BUFFERED_RECORDS: overlapping intervals
// ============================================================================
void test_buffered_overlap() {
    ConcurrentFrameTraceRecorder recorder(ConcurrentTraceMode::kBufferedRecords);

    // Different frames can have overlapping intervals
    expect(recorder.on_stage_begin(0, FrameTraceStage::kSource, 10).ok(), "overlap s0 begin", "must succeed");
    expect(recorder.on_stage_begin(1, FrameTraceStage::kSource, 20).ok(), "overlap s1 begin", "must succeed");
    expect(recorder.on_stage_end(0, FrameTraceStage::kSource, 30).ok(), "overlap s0 end", "must succeed");
    expect(recorder.on_stage_end(1, FrameTraceStage::kSource, 40).ok(), "overlap s1 end", "must succeed");

    // Different stages on same frame can also overlap
    expect(recorder.on_stage_begin(0, FrameTraceStage::kPreprocess, 50).ok(), "overlap pp0 begin", "must succeed");
    expect(recorder.on_stage_begin(0, FrameTraceStage::kInference, 55).ok(), "overlap inf0 begin", "must succeed");
    expect(recorder.on_stage_end(0, FrameTraceStage::kPreprocess, 60).ok(), "overlap pp0 end", "must succeed");
    expect(recorder.on_stage_end(0, FrameTraceStage::kInference, 65).ok(), "overlap inf0 end", "must succeed");

    expect(recorder.records().size() == 4U, "overlap record count", "must have 4 records");
}

// ============================================================================
// Duplicate begin and other error cases
// ============================================================================
void test_buffered_errors() {
    ConcurrentFrameTraceRecorder recorder(ConcurrentTraceMode::kBufferedRecords);

    // Duplicate active interval
    expect(recorder.on_stage_begin(0, FrameTraceStage::kSource, 10).ok(), "err begin s0", "must succeed");
    expect(!recorder.on_stage_begin(0, FrameTraceStage::kSource, 20).ok(),
           "err duplicate begin", "must reject duplicate active interval");
    expect(recorder.on_stage_end(0, FrameTraceStage::kSource, 30).ok(), "err end s0", "must succeed");

    // Duplicate completed interval
    expect(!recorder.on_stage_begin(0, FrameTraceStage::kSource, 40).ok(),
           "err duplicate completed", "must reject duplicate completed interval");

    // No matching end
    expect(!recorder.on_stage_end(0, FrameTraceStage::kInference, 50).ok(),
           "err end no begin", "must reject end without begin");

    // End < begin
    expect(recorder.on_stage_begin(1, FrameTraceStage::kSource, 100).ok(), "err begin s1", "must succeed");
    expect(!recorder.on_stage_end(1, FrameTraceStage::kSource, 50).ok(),
           "err end < begin", "must reject end before begin");

    // Flush with active intervals
    std::ostringstream output;
    expect(!recorder.flush(output).ok(), "err flush active", "must reject flush with active intervals");
    expect(recorder.on_stage_end(1, FrameTraceStage::kSource, 200).ok(), "err end s1", "must succeed");

    // Valid flush
    expect(recorder.flush(output).ok(), "err valid flush", "must succeed");
    expect(recorder.records().size() == 2U, "err record count",
           "must have 2 valid records (frame 0 source + frame 1 source)");
}

// ============================================================================
// BUFFERED_RECORDS retains records
// ============================================================================
void test_buffered_retains_records() {
    ConcurrentFrameTraceRecorder recorder(ConcurrentTraceMode::kBufferedRecords);

    expect(recorder.on_stage_begin(0, FrameTraceStage::kSource, 10).ok() &&
           recorder.on_stage_end(0, FrameTraceStage::kSource, 30).ok(),
           "buffered record", "must succeed");
    expect(recorder.on_stage_begin(0, FrameTraceStage::kPreprocess, 40).ok() &&
           recorder.on_stage_end(0, FrameTraceStage::kPreprocess, 60).ok(),
           "buffered record2", "must succeed");

    expect(recorder.records().size() == 2U, "buffered retains records", "must keep per-frame records");
    expect(recorder.records()[0].cycle_id == 0 &&
           recorder.records()[0].stage == FrameTraceStage::kSource &&
           recorder.records()[0].duration_ns == 20,
           "buffered record detail", "record data mismatch");
}

// ============================================================================
// AGGREGATE_ONLY: no per-frame records, correct aggregates
// ============================================================================
void test_aggregate_only() {
    ConcurrentFrameTraceRecorder recorder(ConcurrentTraceMode::kAggregateOnly);

    expect(recorder.on_stage_begin(0, FrameTraceStage::kSource, 10).ok() &&
           recorder.on_stage_end(0, FrameTraceStage::kSource, 30).ok(),
           "agg s0", "must succeed");
    expect(recorder.on_stage_begin(1, FrameTraceStage::kSource, 40).ok() &&
           recorder.on_stage_end(1, FrameTraceStage::kSource, 100).ok(),
           "agg s1", "must succeed");

    expect(recorder.records().empty(), "agg no records", "AGGREGATE_ONLY must not retain per-frame records");

    const auto& aggregates = recorder.aggregates();
    expect(aggregates.size() == 1U, "agg count", "must have 1 stage aggregate");
    const auto& source_agg = aggregates.at(FrameTraceStage::kSource);
    expect(source_agg.count == 2U, "agg source count", "must be 2");
    expect(source_agg.total_ns == 80U, "agg source total", "20+60=80");
    expect(source_agg.min_ns == 20U, "agg source min", "min must be 20");
    expect(source_agg.max_ns == 60U, "agg source max", "max must be 60");
}

// ============================================================================
// Source-only EOS is not a complete frame
// ============================================================================
void test_source_only_not_complete() {
    ConcurrentFrameTraceRecorder recorder(ConcurrentTraceMode::kBufferedRecords);

    // Only source stage completed
    expect(recorder.on_stage_begin(0, FrameTraceStage::kSource, 10).ok() &&
           recorder.on_stage_end(0, FrameTraceStage::kSource, 30).ok(),
           "source only", "must succeed");

    expect(!recorder.has_complete_frame(0), "source only not complete",
           "single source stage is not a complete frame");
}

// ============================================================================
// Five stages needed for complete frame
// ============================================================================
void test_five_stages_complete() {
    ConcurrentFrameTraceRecorder recorder(ConcurrentTraceMode::kBufferedRecords);

    // Complete all 5 stages for frame 0
    expect(recorder.on_stage_begin(0, FrameTraceStage::kSource, 10).ok() &&
           recorder.on_stage_end(0, FrameTraceStage::kSource, 20).ok() &&
           recorder.on_stage_begin(0, FrameTraceStage::kPreprocess, 30).ok() &&
           recorder.on_stage_end(0, FrameTraceStage::kPreprocess, 40).ok() &&
           recorder.on_stage_begin(0, FrameTraceStage::kInference, 50).ok() &&
           recorder.on_stage_end(0, FrameTraceStage::kInference, 60).ok() &&
           recorder.on_stage_begin(0, FrameTraceStage::kPostprocess, 70).ok() &&
           recorder.on_stage_end(0, FrameTraceStage::kPostprocess, 80).ok() &&
           recorder.on_stage_begin(0, FrameTraceStage::kSink, 90).ok() &&
           recorder.on_stage_end(0, FrameTraceStage::kSink, 100).ok(),
           "five stages", "all must succeed");

    expect(recorder.has_complete_frame(0), "five stages complete", "all 5 stages = complete frame");

    // Frame 1 with only 4 stages should NOT be complete
    expect(recorder.on_stage_begin(1, FrameTraceStage::kSource, 110).ok() &&
           recorder.on_stage_end(1, FrameTraceStage::kSource, 120).ok() &&
           recorder.on_stage_begin(1, FrameTraceStage::kPreprocess, 130).ok() &&
           recorder.on_stage_end(1, FrameTraceStage::kPreprocess, 140).ok() &&
           recorder.on_stage_begin(1, FrameTraceStage::kInference, 150).ok() &&
           recorder.on_stage_end(1, FrameTraceStage::kInference, 160).ok() &&
           recorder.on_stage_begin(1, FrameTraceStage::kPostprocess, 170).ok() &&
           recorder.on_stage_end(1, FrameTraceStage::kPostprocess, 180).ok(),
           "four stages", "all must succeed");

    expect(!recorder.has_complete_frame(1), "four stages not complete",
           "4 stages (missing Sink) is not complete");

    // Unknown frame
    expect(!recorder.has_complete_frame(999), "unknown frame", "should not be complete");
}

// ============================================================================
// Flush with output
// ============================================================================
void test_flush_output() {
    ConcurrentFrameTraceRecorder recorder(ConcurrentTraceMode::kBufferedRecords);

    expect(recorder.on_stage_begin(0, FrameTraceStage::kSource, 10).ok() &&
           recorder.on_stage_end(0, FrameTraceStage::kSource, 30).ok(),
           "flush setup", "must succeed");

    std::ostringstream output;
    expect(recorder.flush(output).ok(), "flush output", "must succeed");
    const std::string text = output.str();
    expect(text.find("\"cycle_id\":0") != std::string::npos, "flush output content", "missing cycle_id");
    expect(text.find("\"stage\":\"source\"") != std::string::npos, "flush stage name", "missing stage name");
    expect(text.find("\"duration_ns\":20") != std::string::npos, "flush duration", "missing duration");
}

// ============================================================================
// AGGREGATE_ONLY with new data keeps aggregates, empty records in flush
// ============================================================================
void test_aggregate_flush_empty_records() {
    ConcurrentFrameTraceRecorder recorder(ConcurrentTraceMode::kAggregateOnly);

    expect(recorder.on_stage_begin(0, FrameTraceStage::kInference, 10).ok() &&
           recorder.on_stage_end(0, FrameTraceStage::kInference, 110).ok(),
           "agg flush setup", "must succeed");

    std::ostringstream output;
    expect(recorder.flush(output, false).ok(), "agg flush", "must succeed");
    // AGGREGATE_ONLY produces no per-frame JSON records
    expect(output.str().empty(), "agg flush empty", "AGGREGATE_ONLY flush must produce no records");

    const auto& aggs = recorder.aggregates();
    expect(aggs.at(FrameTraceStage::kInference).count == 1U, "agg count after flush", "count must be 1");
}

}  // namespace

int main() {
    test_trace_recorder_regression();
    test_buffered_overlap();
    test_buffered_errors();
    test_buffered_retains_records();
    test_aggregate_only();
    test_source_only_not_complete();
    test_five_stages_complete();
    test_flush_output();
    test_aggregate_flush_empty_records();

    if (failures != 0) {
        std::cerr << failures << " Concurrent frame trace test(s) failed\n";
        return 1;
    }
    std::cout << "Concurrent frame trace tests passed\n";
    return 0;
}
