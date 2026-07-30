#include "edge_ai_defect/runtime/canonical_detection_hash.hpp"

#include <cmath>
#include <iostream>
#include <limits>
#include <iomanip>
#include <sstream>
#include <string>

using namespace edge_ai_defect;

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

runtime::FrameResult make_frame(std::size_t seq, const std::string& path,
                                 int w, int h,
                                 std::vector<postprocess::Detection> dets) {
    runtime::FrameResult f;
    f.sequence_index = seq;
    f.relative_path = path;
    f.image_width = w;
    f.image_height = h;
    f.detections = std::move(dets);
    return f;
}

void test_empty_vector() {
    std::vector<std::uint8_t> bytes;
    expect(runtime::serialize_canonical_detections(runtime::CanonicalScope::kRun, {}, &bytes).ok(),
           "empty vector", "must succeed");
    expect(bytes.size() == 8U + 4U + 4U + 8U + 8U, "empty vector size",
           "expected 32 bytes for empty vector");

    std::ostringstream hex_out;
    hex_out << std::hex << std::setfill('0');
    for (std::uint8_t v : bytes) hex_out << std::setw(2) << static_cast<unsigned>(v);
    expect(hex_out.str() == "45414943414e4f4e010000000100000000000000000000000000000000000000",
           "empty vector hex", "golden hex mismatch: " + hex_out.str());

    std::string empty_hash;
    expect(runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, {}, &empty_hash).ok(),
           "empty vector sha256", "must succeed");
    expect(empty_hash == "f48f8ba534f74ee56cdb1b884c182afe0af7dbf7667219e8eb32dc769649d39d",
           "empty vector sha256 golden", "mismatch: " + empty_hash);
}

void test_non_empty_fixed_vector() {
    // Non-empty vector with: non-zero sequence index, UTF-8 path, positive w/h,
    // 2+ detections, different candidate_index, different class_id, normal float, -0.0 float.
    std::vector<runtime::FrameResult> frames;
    frames.push_back(make_frame(42, "中文/嵌套/test.jpg", 640, 480, {
        {10.5F, 20.25F, 100.0F, 200.0F, 0.95F, 0, 7},      // class_id=0, candidate=7
        {-0.0F, 1.0F, 2.0F, 3.0F, 0.5F, 1, 123},           // class_id=1, candidate=123, x1=-0.0
    }));

    // RUN scope: uses sequence_index=42
    std::vector<std::uint8_t> run_bytes;
    expect(runtime::serialize_canonical_detections(runtime::CanonicalScope::kRun, frames, &run_bytes).ok(),
           "non-empty RUN serialize", "must succeed");

    std::ostringstream run_hex;
    run_hex << std::hex << std::setfill('0');
    for (std::uint8_t v : run_bytes) run_hex << std::setw(2) << static_cast<unsigned>(v);
    const std::string expected_run_hex =
        "45414943414e4f4e01000000010000002a00000000000000"
        "16000000"  // path length = 22 (UTF-8 "中文/嵌套/test.jpg")
        "e4b8ade696872fe5b58ce5a5972f746573742e6a7067"
        "80020000e0010000"
        "02000000"
        "0700000000000000"
        "00000000"
        "3333733f"  // confidence 0.95
        "00002841"  // x1=10.5
        "0000a241"  // y1=20.25
        "0000c842"  // x2=100.0
        "00004843"  // y2=200.0
        "7b00000000000000"
        "01000000"
        "0000003f"  // confidence 0.5
        "00000080"  // x1=-0.0
        "0000803f"  // y1=1.0
        "00000040"  // x2=2.0
        "00004040"  // y2=3.0
        "0100000000000000"
        "0200000000000000";
    expect(run_hex.str() == expected_run_hex,
           "non-empty RUN hex golden", "mismatch:\nexpected: " + expected_run_hex + "\n  actual: " + run_hex.str());

    std::string run_hash;
    expect(runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, frames, &run_hash).ok(),
           "non-empty RUN sha256", "must succeed");
    expect(run_hash == "8140a5c538bfed9c02197d3921e4b2d5e367d01ef43d373795cfdfed0a969bc3",
           "non-empty RUN sha256 golden", "mismatch: " + run_hash);

    // CYCLE scope: uses zero-based index (0) instead of sequence_index (42)
    std::vector<std::uint8_t> cycle_bytes;
    expect(runtime::serialize_canonical_detections(runtime::CanonicalScope::kCycle, frames, &cycle_bytes).ok(),
           "non-empty CYCLE serialize", "must succeed");

    std::ostringstream cycle_hex;
    cycle_hex << std::hex << std::setfill('0');
    for (std::uint8_t v : cycle_bytes) cycle_hex << std::setw(2) << static_cast<unsigned>(v);
    const std::string expected_cycle_hex =
        "45414943414e4f4e0100000002"
        "0000000000000000000000"
        "16000000"
        "e4b8ade696872fe5b58ce5a5972f746573742e6a7067"
        "80020000e0010000"
        "02000000"
        "0700000000000000"
        "00000000"
        "3333733f"
        "00002841"
        "0000a241"
        "0000c842"
        "00004843"
        "7b00000000000000"
        "01000000"
        "0000003f"
        "00000080"
        "0000803f"
        "00000040"
        "00004040"
        "0100000000000000"
        "0200000000000000";
    expect(cycle_hex.str() == expected_cycle_hex,
           "non-empty CYCLE hex golden", "mismatch:\nexpected: " + expected_cycle_hex + "\n  actual: " + cycle_hex.str());

    std::string cycle_hash;
    expect(runtime::canonical_detection_sha256(runtime::CanonicalScope::kCycle, frames, &cycle_hash).ok(),
           "non-empty CYCLE sha256", "must succeed");
    expect(cycle_hash == "76b966b4cfa937a64009b611b37133564f04cc71088d648eb7861c65c3abc059",
           "non-empty CYCLE sha256 golden", "mismatch: " + cycle_hash);

    // RUN and CYCLE must differ
    expect(run_hash != cycle_hash, "RUN vs CYCLE domain separation", "hashes must differ");
}

void test_cross_cycle() {
    // Cycle A: frames with global sequence 0...N-1
    // Cycle B: same paths/dimensions/detections but with global sequence offset (e.g. 180...180+N-1)
    // RUN_SHA_A != RUN_SHA_B  (different global sequences)
    // CYCLE_SHA_A == CYCLE_SHA_B (same zero-based positions)

    auto make = [](std::size_t seq) {
        return make_frame(seq, "img.png", 320, 240, {
            {10.0F, 20.0F, 30.0F, 40.0F, 0.99F, 0, 1},
        });
    };

    const std::vector<runtime::FrameResult> cycle_a = {make(0), make(1), make(2)};
    const std::vector<runtime::FrameResult> cycle_b = {make(180), make(181), make(182)};

    std::string run_a, run_b, cycle_a_hash, cycle_b_hash;
    expect(runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, cycle_a, &run_a).ok(),
           "cross-cycle RUN A", "must succeed");
    expect(runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, cycle_b, &run_b).ok(),
           "cross-cycle RUN B", "must succeed");
    expect(runtime::canonical_detection_sha256(runtime::CanonicalScope::kCycle, cycle_a, &cycle_a_hash).ok(),
           "cross-cycle CYCLE A", "must succeed");
    expect(runtime::canonical_detection_sha256(runtime::CanonicalScope::kCycle, cycle_b, &cycle_b_hash).ok(),
           "cross-cycle CYCLE B", "must succeed");

    expect(run_a != run_b, "cross-cycle RUN different", "global sequence offset must produce different hashes");
    expect(cycle_a_hash == cycle_b_hash, "cross-cycle CYCLE identical", "cycle position must produce identical hashes");
}

void test_domain_separation() {
    auto f = make_frame(0, "a.jpg", 10, 20, {{-0.0F, 1.0F, 2.0F, 3.0F, 0.5F, 0, 4}});
    std::vector<runtime::FrameResult> frames{f};

    std::string run_hash, cycle_hash;
    expect(runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, frames, &run_hash).ok() &&
           runtime::canonical_detection_sha256(runtime::CanonicalScope::kCycle, frames, &cycle_hash).ok(),
           "domain separation", "must succeed");
    expect(run_hash != cycle_hash, "domain separation hash differ", "RUN and CYCLE must produce different hashes");
    expect(run_hash.size() == 64U, "domain separation RUN length", "must be 64 hex chars");
    expect(cycle_hash.size() == 64U, "domain separation CYCLE length", "must be 64 hex chars");
}

void test_plus_minus_zero() {
    auto f_pos = make_frame(0, "a.jpg", 10, 20, {{0.0F, 1.0F, 2.0F, 3.0F, 0.5F, 0, 4}});
    auto f_neg = make_frame(0, "a.jpg", 10, 20, {{-0.0F, 1.0F, 2.0F, 3.0F, 0.5F, 0, 4}});

    std::string pos_hash, neg_hash;
    expect(runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, {f_pos}, &pos_hash).ok() &&
           runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, {f_neg}, &neg_hash).ok(),
           "+0/-0 compute", "must succeed");
    expect(pos_hash != neg_hash, "+0/-0 different hash", "+0.0 and -0.0 must produce different hashes");
}

void test_nan_rejected() {
    auto f = make_frame(0, "a.jpg", 10, 20, {});
    f.detections.push_back({std::numeric_limits<float>::quiet_NaN(), 1.0F, 2.0F, 3.0F, 0.5F, 0, 4});
    std::string hash;
    expect(!runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, {f}, &hash).ok(),
           "NaN rejected", "must fail");
}

void test_pos_inf_rejected() {
    auto f = make_frame(0, "a.jpg", 10, 20, {});
    f.detections.push_back({std::numeric_limits<float>::infinity(), 1.0F, 2.0F, 3.0F, 0.5F, 0, 4});
    std::string hash;
    expect(!runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, {f}, &hash).ok(),
           "+Inf rejected", "must fail");
}

void test_neg_inf_rejected() {
    auto f = make_frame(0, "a.jpg", 10, 20, {});
    f.detections.push_back({-std::numeric_limits<float>::infinity(), 1.0F, 2.0F, 3.0F, 0.5F, 0, 4});
    std::string hash;
    expect(!runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, {f}, &hash).ok(),
           "-Inf rejected", "must fail");
}

void test_null_output_rejected() {
    expect(!runtime::serialize_canonical_detections(runtime::CanonicalScope::kRun, {}, nullptr).ok(),
           "null output serialize", "must fail");
    expect(!runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, {}, nullptr).ok(),
           "null output sha256", "must fail");
}

void test_invalid_scope_rejected() {
    std::vector<std::uint8_t> bytes;
    expect(!runtime::serialize_canonical_detections(static_cast<runtime::CanonicalScope>(99), {}, &bytes).ok(),
           "invalid scope serialize", "must fail");
    std::string hash;
    expect(!runtime::canonical_detection_sha256(static_cast<runtime::CanonicalScope>(99), {}, &hash).ok(),
           "invalid scope sha256", "must fail");
}

void test_detection_order_preserved() {
    // Verify detection order is strictly preserved in the hash output
    auto f1 = make_frame(0, "a.jpg", 100, 200, {
        {1.0F, 2.0F, 3.0F, 4.0F, 0.9F, 0, 10},
        {5.0F, 6.0F, 7.0F, 8.0F, 0.8F, 1, 20},
    });
    auto f2 = make_frame(0, "a.jpg", 100, 200, {
        {5.0F, 6.0F, 7.0F, 8.0F, 0.8F, 1, 20},
        {1.0F, 2.0F, 3.0F, 4.0F, 0.9F, 0, 10},
    });
    std::string h1, h2;
    expect(runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, {f1}, &h1).ok() &&
           runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, {f2}, &h2).ok(),
           "detection order compute", "must succeed");
    expect(h1 != h2, "detection order preserved", "reversed detections must produce different hashes");
}

}  // namespace

int main() {
    test_empty_vector();
    test_non_empty_fixed_vector();
    test_cross_cycle();
    test_domain_separation();
    test_plus_minus_zero();
    test_nan_rejected();
    test_pos_inf_rejected();
    test_neg_inf_rejected();
    test_null_output_rejected();
    test_invalid_scope_rejected();
    test_detection_order_preserved();

    if (failures != 0) {
        std::cerr << failures << " Canonical detection hash test(s) failed\n";
        return 1;
    }
    std::cout << "Canonical detection hash tests passed\n";
    return 0;
}
