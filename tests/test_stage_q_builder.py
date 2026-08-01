#!/usr/bin/env python3
"""Focused Q2 contract tests; no benchmark and no formal calibration."""
import json
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILDER = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "build-q2/stage_q_int8_builder"
MANIFEST = ROOT / "results/validation/stage_q/split_v2_deduplicated/train_manifest_v2.json"
DATASET = ROOT / "data/raw/NEU-DET"


def run(*args):
    return subprocess.run([str(BUILDER), *map(str, args)], text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main():
    parsed = json.loads(MANIFEST.read_text())
    assert parsed["split"] == "train" and len(parsed["entries"]) == 1260
    assert len({entry["image_sha256"] for entry in parsed["entries"]}) == 1260

    with tempfile.TemporaryDirectory(prefix="stage-q-test-") as temp:
        duplicate = pathlib.Path(temp) / "duplicate.json"
        data = json.loads(MANIFEST.read_text())
        data["entries"][1]["image_sha256"] = data["entries"][0]["image_sha256"]
        duplicate.write_text(json.dumps(data))
        failed = run("--artifact-purpose", "smoke", "--cache-mode", "force-miss", f"--manifest={duplicate}",
                     f"--dataset-root={DATASET}")
        assert failed.returncode != 0 and "duplicate" in failed.stderr.lower()

        output = pathlib.Path(temp) / "published"
        wrong = run("--artifact-purpose", "smoke", "--cache-mode", "force-miss",
                    f"--manifest={duplicate}", f"--dataset-root={DATASET}",
                    f"--output={output}")
        assert wrong.returncode != 0 and not output.exists(), wrong.stderr

    source = (ROOT / "src/stage_q_int8_builder.cpp").read_text()
    for key in ("schema_version", "artifact_purpose", "cache_sha256",
                "onnx_sha256", "model_contract_sha256",
                "calibration_manifest_sha256", "builder_executable_sha256"):
        assert key in source, key
    print("STAGE_Q_BUILDER_FOCUSED_TESTS_PASS")


if __name__ == "__main__":
    main()
