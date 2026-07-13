from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_export_module():
    module_path = REPO_ROOT / "scripts" / "export_onnx.py"
    spec = importlib.util.spec_from_file_location("export_onnx", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


export_onnx = load_export_module()


class ExportConfigTest(unittest.TestCase):
    def valid_config(self, root: Path) -> dict[str, object]:
        source_model = root / "model.pt"
        source_model.write_bytes(b"checkpoint")
        return {
            "source_model": str(source_model),
            "onnx_path": str(root / "model.onnx"),
            "metadata_path": str(root / "metadata.json"),
            "imgsz": 640,
            "opset": 17,
            "dynamic": False,
            "simplify": False,
        }

    def test_validate_config_accepts_complete_config(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            export_onnx.validate_config(self.valid_config(Path(temp_dir)))

    def test_validate_config_rejects_non_boolean_dynamic(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config = self.valid_config(Path(temp_dir))
            config["dynamic"] = "false"
            with self.assertRaisesRegex(ValueError, "dynamic.*boolean"):
                export_onnx.validate_config(config)

    def test_dry_run_plan_has_hash_and_does_not_create_outputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config = self.valid_config(root)
            plan = export_onnx.export_plan(config)

            self.assertEqual(
                plan["source_model_sha256"], export_onnx.sha256_file(root / "model.pt")
            )
            self.assertFalse((root / "model.onnx").exists())
            self.assertFalse((root / "metadata.json").exists())

    def test_export_model_forwards_yaml_options_and_moves_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config = self.valid_config(root)
            calls = []

            class FakeYOLO:
                def __init__(self, model_path):
                    self.model_path = Path(model_path)

                def export(self, **kwargs):
                    calls.append(kwargs)
                    exported = self.model_path.with_suffix(".onnx")
                    exported.write_bytes(b"onnx")
                    return str(exported)

            output_path = export_onnx.export_model(config, FakeYOLO)

            self.assertEqual(output_path, root / "model.onnx")
            self.assertEqual(output_path.read_bytes(), b"onnx")
            self.assertEqual(
                calls,
                [
                    {
                        "format": "onnx",
                        "imgsz": 640,
                        "opset": 17,
                        "dynamic": False,
                        "simplify": False,
                    }
                ],
            )


class MetadataTest(unittest.TestCase):
    def test_write_metadata_records_required_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_model = root / "model.pt"
            onnx_path = root / "model.onnx"
            source_model.write_bytes(b"checkpoint")
            onnx_path.write_bytes(b"onnx")
            config = {
                "source_model": str(source_model),
                "onnx_path": str(onnx_path),
                "metadata_path": str(root / "metadata.json"),
                "imgsz": 640,
                "opset": 17,
                "dynamic": False,
                "simplify": False,
            }

            with mock.patch.object(
                export_onnx, "timestamp", return_value="2026-07-13T12:00:00+08:00"
            ):
                metadata_path = export_onnx.write_metadata(config, onnx_path, "8.4.50", "2.3.1")
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

            self.assertEqual(
                set(metadata),
                {
                    "source_model_path",
                    "source_model_sha256",
                    "onnx_path",
                    "onnx_sha256",
                    "imgsz",
                    "opset",
                    "dynamic",
                    "simplify",
                    "ultralytics_version",
                    "torch_version",
                    "timestamp",
                },
            )
            self.assertEqual(metadata["onnx_sha256"], export_onnx.sha256_file(onnx_path))


if __name__ == "__main__":
    unittest.main()
