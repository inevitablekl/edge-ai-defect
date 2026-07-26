#!/usr/bin/env python3
"""Deterministic Stage J Level B raw-output analyzer."""

import argparse
import hashlib
import json
import math
import struct
from collections import OrderedDict

COUNT = 84000
CHANNELS = 10
CANDIDATES = 8400


def read_values(path):
    data = open(path, "rb").read()
    return data, list(struct.unpack("<%df" % (len(data) // 4), data)) if len(data) % 4 == 0 else []


def finite_counts(values):
    return OrderedDict([
        ("finite_count", sum(math.isfinite(x) for x in values)),
        ("nan_count", sum(math.isnan(x) for x in values)),
        ("positive_inf_count", sum(math.isinf(x) and x > 0 for x in values)),
        ("negative_inf_count", sum(math.isinf(x) and x < 0 for x in values)),
    ])


def number(value):
    return value if math.isfinite(value) else None


def compare(golden, actual, indices):
    indices = list(indices)
    differences = []
    absolute_sum = 0.0
    for index in indices:
        left, right = golden[index], actual[index]
        if not math.isfinite(left) or not math.isfinite(right):
            differences.append((math.inf, index, left, right))
        else:
            difference = abs(float(left) - float(right))
            absolute_sum += difference
            differences.append((difference, index, left, right))
    maximum = max(differences, key=lambda item: (item[0], -item[1])) if differences else (0.0, 0, 0.0, 0.0)
    return OrderedDict([
        ("element_count", len(indices)),
        ("mae", number(absolute_sum / len(indices)) if indices else None),
        ("max_abs", number(maximum[0])),
        ("max_error_flat_index", maximum[1]),
        ("golden_value", number(maximum[2])),
        ("actual_value", number(maximum[3])),
    ])


def analyze(golden_bytes, golden, actual_bytes, actual):
    valid_count = len(golden) == COUNT and len(actual) == COUNT
    if valid_count:
        overall = compare(golden, actual, range(COUNT))
        bbox = compare(golden, actual, (channel * CANDIDATES + candidate for channel in range(4) for candidate in range(CANDIDATES)))
        score = compare(golden, actual, (channel * CANDIDATES + candidate for channel in range(4, 10) for candidate in range(CANDIDATES)))
        per_channel = []
        for channel in range(CHANNELS):
            item = compare(golden, actual, range(channel * CANDIDATES, (channel + 1) * CANDIDATES))
            item["channel"] = channel
            item["semantic_group"] = "bbox" if channel < 4 else "score"
            item.move_to_end("channel", last=False)
            item.move_to_end("semantic_group", last=False)
            item["max_candidate"] = item.pop("max_error_flat_index") % CANDIDATES
            per_channel.append(item)
        overall["max_error_channel"] = overall["max_error_flat_index"] // CANDIDATES
        overall["max_error_candidate"] = overall["max_error_flat_index"] % CANDIDATES
    else:
        overall = OrderedDict([(key, None) for key in ("element_count", "mae", "max_abs", "max_error_flat_index", "max_error_channel", "max_error_candidate", "golden_value", "actual_value")])
        bbox = OrderedDict([(key, None) for key in ("element_count", "mae", "max_abs", "max_error_flat_index", "golden_value", "actual_value")])
        score = OrderedDict([(key, None) for key in ("element_count", "mae", "max_abs", "max_error_flat_index", "golden_value", "actual_value")])
        per_channel = []
    finite = valid_count and all(math.isfinite(x) for x in golden + actual)
    stage_pass = bool(valid_count and finite and overall["mae"] <= 1e-6 and overall["max_abs"] <= 1e-4)
    strict = bool(valid_count and finite and overall["mae"] <= 1e-6 and overall["max_abs"] <= 1e-5)
    return OrderedDict([
        ("schema_version", 1),
        ("shape", [1, 10, 8400]),
        ("element_count", COUNT),
        ("overall", overall),
        ("bbox_group", bbox),
        ("score_group", score),
        ("per_channel", per_channel),
        ("golden", OrderedDict([("sha256", hashlib.sha256(golden_bytes).hexdigest()), *finite_counts(golden).items()])),
        ("actual", OrderedDict([("sha256", hashlib.sha256(actual_bytes).hexdigest()), *finite_counts(actual).items()])),
        ("stage_j_pass", stage_pass),
        ("m2_strict_equivalent", strict),
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--golden", required=True)
    parser.add_argument("--actual", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    golden_bytes, golden = read_values(args.golden)
    actual_bytes, actual = read_values(args.actual)
    report = analyze(golden_bytes, golden, actual_bytes, actual)
    with open(args.report, "w", encoding="utf-8", newline="\n") as output:
        json.dump(report, output, ensure_ascii=True, indent=2, separators=(",", ": "), allow_nan=False)
        output.write("\n")
    return 0 if report["stage_j_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
