#!/usr/bin/env python3
"""M4.5 subprocess smoke tests for the public edge_ai_defect executable."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import sys


POSTPROCESS = """postprocess:
  confidence_threshold: 0.25
  iou_threshold: 0.45
  max_nms: 30000
  max_det: 300
  max_wh: 7680.0
  agnostic: false
  multi_label: false
timing:
  enabled: false
"""


def run(executable, arguments, expected_code):
    result = subprocess.run(
        [str(executable), *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != expected_code:
        raise AssertionError(
            f"{arguments!r}: expected exit {expected_code}, got {result.returncode}; "
            f"stdout={result.stdout!r}; stderr={result.stderr!r}"
        )
    return result


def yaml_quote(path):
    return '"' + str(path).replace('\\', '/').replace('"', '\\"') + '"'


def write_config(path, contract_path, model_path, input_directory, json_path,
                 console=False, overwrite=True):
    path.write_text(
        "schema_version: 1\n"
        "backend:\n  type: onnxruntime_cpu\n"
        "model:\n"
        f"  contract_path: {yaml_quote(contract_path)}\n"
        f"  model_path: {yaml_quote(model_path)}\n"
        "input:\n"
        "  type: directory\n"
        f"  directory: {yaml_quote(input_directory)}\n"
        "output:\n"
        f"  json_path: {yaml_quote(json_path)}\n"
        f"  console: {'true' if console else 'false'}\n"
        f"  overwrite: {'true' if overwrite else 'false'}\n"
        + POSTPROCESS,
        encoding="utf-8",
    )


def write_bmp(path, width, height, bgr):
    """Write deterministic uncompressed 24-bit BMP without an image-library dependency."""
    row_bytes = width * 3
    padding = b"\x00" * ((4 - row_bytes % 4) % 4)
    pixels = (bytes(bgr) * width + padding) * height
    file_size = 14 + 40 + len(pixels)
    header = struct.pack(
        "<2sIHHI", b"BM", file_size, 0, 0, 54
    ) + struct.pack(
        "<IIIHHIIIIII", 40, width, height, 1, 24, 0, len(pixels),
        2835, 2835, 0, 0
    )
    path.write_bytes(header + pixels)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def verify_json(path, expected_names, expected_sizes):
    raw = path.read_bytes()
    parsed = json.loads(raw.decode("utf-8"))
    require(set(parsed) == {"schema_version", "backend", "model", "postprocess", "images", "summary"},
            "unexpected top-level JSON schema")
    require(parsed["schema_version"] == 1, "wrong schema_version")
    require(parsed["backend"] == {"type": "onnxruntime_cpu"}, "wrong backend")
    model = parsed["model"]
    require(model["filename"] == "yolov8n_neudet_frozen.onnx", "wrong model filename")
    require(model["sha256"] == "c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944",
            "wrong model SHA")
    require(model["contract_filename"] == "yolov8n_neudet_frozen.yaml", "wrong contract filename")
    require(model["classes"] == ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"],
            "wrong class ordering")
    postprocess = parsed["postprocess"]
    require(math.isclose(postprocess["confidence_threshold"], 0.25, abs_tol=1e-6),
            "wrong confidence_threshold metadata")
    require(math.isclose(postprocess["iou_threshold"], 0.45, abs_tol=1e-6),
            "wrong iou_threshold metadata")
    require({key: postprocess[key] for key in ("max_nms", "max_det", "max_wh", "agnostic", "multi_label")} == {
        "max_nms": 30000, "max_det": 300, "max_wh": 7680,
        "agnostic": False, "multi_label": False,
    }, "wrong discrete postprocess metadata")
    images = parsed["images"]
    require(len(images) == len(expected_names), "wrong image count")
    total_detections = 0
    for index, (image, name, size) in enumerate(zip(images, expected_names, expected_sizes)):
        require(image["sequence_index"] == index, "non-contiguous sequence index")
        require(image["relative_path"] == name and not Path(image["relative_path"]).is_absolute(),
                "wrong or absolute relative path")
        require((image["width"], image["height"]) == size, "wrong image dimensions")
        require("timing_ms" not in image and isinstance(image["detections"], list),
                "timing or detections schema violation")
        for detection in image["detections"]:
            require(0 <= detection["class_id"] < 6 and 0 <= detection["candidate_index"] < 8400,
                    "invalid detection identifiers")
            for field in ("confidence", "x1", "y1", "x2", "y2"):
                require(math.isfinite(detection[field]), "non-finite detection value")
            require(0.0 <= detection["x1"] <= size[0] and 0.0 <= detection["x2"] <= size[0],
                    "x coordinate outside image")
            require(0.0 <= detection["y1"] <= size[1] and 0.0 <= detection["y2"] <= size[1],
                    "y coordinate outside image")
        total_detections += len(image["detections"])
    require(parsed["summary"] == {"processed_images": len(images), "total_detections": total_detections},
            "wrong summary")
    require(b"timestamp" not in raw and b"fps" not in raw.lower() and b"percentile" not in raw.lower(),
            "non-functional metadata present")
    return raw


def run_off(arguments):
    root = Path(arguments.temp_dir) / "application_off"
    root.mkdir(parents=True, exist_ok=True)
    executable = Path(arguments.executable)

    help_result = run(executable, ["--help"], 0)
    require(help_result.stdout == "Usage: edge_ai_defect --config <runtime.yaml>\n" and not help_result.stderr,
            "help stdout/stderr contract violated")
    for argv in (
            [], ["-h"], ["--unknown"], ["input.yaml"], ["--config"],
            ["--config", "one.yaml", "--config", "two.yaml"],
            ["--config", "one.yaml", "extra"], ["--help", "--config", "x.yaml"]):
        result = run(executable, argv, 2)
        require(result.stderr.startswith("error: "), "CLI error must use stderr")
    run(executable, ["--config", str(root / "missing.yaml")], 2)

    schema_error = root / "schema_error.yaml"
    schema_error.write_text("schema_version: 1\nunknown: true\n", encoding="utf-8")
    run(executable, ["--config", str(schema_error)], 2)

    missing_contract = root / "missing_contract.yaml"
    write_config(missing_contract, root / "missing_contract.yaml", root / "missing.onnx",
                 root / "missing_input", root / "result.json")
    run(executable, ["--config", str(missing_contract)], 3)

    missing_input = root / "missing_input.yaml"
    write_config(missing_input, Path(arguments.contract), root / "missing.onnx",
                 root / "missing_input", root / "result.json")
    run(executable, ["--config", str(missing_input)], 3)


def run_on(arguments):
    root = Path(arguments.temp_dir) / "application_on"
    images = root / "images"
    images.mkdir(parents=True, exist_ok=True)
    write_bmp(images / "a_smoke.bmp", 3, 2, (7, 5, 3))
    write_bmp(images / "z_smoke.bmp", 2, 4, (40, 30, 20))
    expected_names = ["a_smoke.bmp", "z_smoke.bmp"]
    expected_sizes = [(3, 2), (2, 4)]
    executable = Path(arguments.executable)
    result_path = root / "result.json"
    config = root / "runtime_smoke.yaml"
    write_config(config, Path(arguments.contract), Path(arguments.model), images, result_path)

    run(executable, ["--config", str(config)], 0)
    first = verify_json(result_path, expected_names, expected_sizes)
    first_sha256 = hashlib.sha256(first).hexdigest()
    run(executable, ["--config", str(config)], 0)
    second = verify_json(result_path, expected_names, expected_sizes)
    require(first == second and first_sha256 == hashlib.sha256(second).hexdigest(),
            "timing-disabled JSON is not byte-identical across overwrite run")

    console_path = root / "console.json"
    console_config = root / "console_smoke.yaml"
    write_config(console_config, Path(arguments.contract), Path(arguments.model), images,
                 console_path, console=True)
    console = run(executable, ["--config", str(console_config)], 0)
    require("RUN backend=onnxruntime_cpu" in console.stdout and
            console.stdout.count("IMAGE index=") == 2 and
            "SUMMARY processed_images=2" in console.stdout and
            "_ms=" not in console.stdout and not console.stderr,
            "console smoke output contract violated")
    verify_json(console_path, expected_names, expected_sizes)

    missing_parent = root / "missing_parent" / "result.json"
    bad_output_config = root / "bad_output.yaml"
    write_config(bad_output_config, Path(arguments.contract), Path(arguments.model), images,
                 missing_parent)
    run(executable, ["--config", str(bad_output_config)], 3)
    require(not missing_parent.exists(), "failed run left a final JSON target")

    overwrite_false = root / "overwrite_false.yaml"
    write_config(overwrite_false, Path(arguments.contract), Path(arguments.model), images,
                 result_path, overwrite=False)
    run(executable, ["--config", str(overwrite_false)], 3)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("off", "on"), required=True)
    parser.add_argument("--executable", required=True)
    parser.add_argument("--temp-dir", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--model")
    arguments = parser.parse_args()
    if arguments.mode == "on":
        require(arguments.model is not None, "--model is required for ON smoke")
        run_on(arguments)
    else:
        run_off(arguments)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"application smoke failed: {error}", file=sys.stderr)
        sys.exit(1)
