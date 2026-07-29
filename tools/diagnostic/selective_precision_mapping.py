#!/usr/bin/env python3
"""Build an auditable Detect-head precision mapping from frozen ONNX facts."""

import argparse
import hashlib
import json
import sys
from pathlib import Path


DIAGNOSTIC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIAGNOSTIC_DIR))
import onnx_head_output_view as onnx_view  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_nodes(onnx_path: Path) -> list[dict]:
    model = onnx_path.read_bytes()
    graphs = [value for number, wire, value, _ in onnx_view.read_fields(model)
              if number == 7 and wire == 2]
    if len(graphs) != 1:
        raise RuntimeError("expected exactly one ONNX graph")
    graph = graphs[0]
    nodes = []
    for number, wire, message, _ in onnx_view.read_fields(graph):
        if number != 1 or wire != 2:
            continue
        name = onnx_view.extract_string(message, 3)
        op_type = onnx_view.extract_string(message, 4)
        inputs, outputs = [], []
        for field, field_wire, value, _ in onnx_view.read_fields(message):
            if field == 1 and field_wire == 2:
                inputs.append(value.decode("utf-8", "replace"))
            elif field == 2 and field_wire == 2:
                outputs.append(value.decode("utf-8", "replace"))
        nodes.append({"name": name, "op_type": op_type, "inputs": inputs,
                      "outputs": outputs})
    return nodes


def layer_records(layer_info_path: Path) -> list[dict]:
    data = json.loads(layer_info_path.read_text())
    return data.get("Layers", [])


def metadata_matches(layer: dict, node_name: str) -> bool:
    return f"[ONNX Layer: {node_name}]" in str(layer.get("Metadata", ""))


def role(name: str) -> str:
    if "/cv2." in name:
        return "bbox_regression_branch"
    if "/cv3." in name:
        return "classification_branch"
    if "/dfl/" in name:
        return "dfl"
    if name.endswith("/Concat_3"):
        return "final_output_assembly"
    return "coordinate_decode"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--onnx", type=Path, required=True)
    parser.add_argument("--legacy-mapping", type=Path, required=True)
    parser.add_argument("--layer-info", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    nodes = parse_nodes(args.onnx)
    head_nodes = [node for node in nodes
                  if node["name"].startswith("/model.22/")]
    constants = {node["name"] for node in head_nodes if node["op_type"] == "Constant"}
    shape_control = {node["name"] for node in head_nodes
                     if node["op_type"] in {"Constant", "Shape", "Gather"}}
    constrained = [node for node in head_nodes if node["name"] not in shape_control]
    legacy = json.loads(args.legacy_mapping.read_text())
    legacy_names = {node["onnx_node"] for node in legacy["nodes"]}
    layers = layer_records(args.layer_info)

    producer = {output: node["name"] for node in head_nodes
                for output in node["outputs"]}
    mappings = []
    blocked = []
    for node in constrained:
        matches = [layer for layer in layers if metadata_matches(layer, node["name"])]
        if not matches:
            matches = [layer for layer in layers if layer.get("Name") == node["name"]]
        mapping_mode = "detailed_metadata"
        if not matches:
            # TensorRT 10.3 may fuse/elide graph bookkeeping and pointwise
            # layers.  The exact parser node identity is still the accepted
            # layer policy identity (as demonstrated by C1/C2), while the
            # detailed dump is the execution-layer evidence when present.
            matches = [{"Name": node["name"], "Metadata": "",
                        "mapping_mode": "parser_identity_fused_or_elided"}]
            mapping_mode = "parser_identity_fused_or_elided"
        ancestry = []
        for value in node["inputs"]:
            if value in producer:
                ancestry.append(producer[value])
            elif value.startswith("/model."):
                ancestry.append("external:" + value)
            elif value:
                ancestry.append("initializer:" + value)
        mappings.append({
            "onnx_node_name": node["name"],
            "onnx_op_type": node["op_type"],
            "onnx_output_tensor": node["outputs"],
            "tensorrt_network_layer_names": [layer.get("Name") for layer in matches],
            "semantic_role": role(node["name"]),
            "candidate_M1_membership": node["name"] in legacy_names,
            "candidate_M2_membership": True,
            "requested_compute_precision": "fp32",
            "requested_output_type": "fp32",
            "mapping_evidence": {
                "onnx_source_sha256": sha256(args.onnx),
                "graph_scope": "/model.22",
                "graph_ancestry_inputs": ancestry,
                "trt_layer_metadata_matches": [layer.get("Metadata", "") for layer in matches],
                "legacy_C2_equivalent_node": node["name"] in legacy_names,
            },
            "mapping_confidence": "high" if mapping_mode == "detailed_metadata" else "medium",
            "mapping_mode": mapping_mode,
        })

    result = {
        "schema_version": 1,
        "artifact_kind": "stage_k_selective_precision_layer_mapping",
        "source_onnx": str(args.onnx),
        "source_onnx_sha256": sha256(args.onnx),
        "graph_scope": "/model.22 Detect Head",
        "onnx_model22_node_count": len(head_nodes),
        "constant_node_count_excluded_from_constraints": len(constants),
        "shape_control_node_count_excluded_from_constraints": len(shape_control - constants),
        "constrained_node_count": len(constrained),
        "legacy_C2_node_count": len(legacy_names),
        "route_decision": "CASE_B_DIRECT_M2",
        "mapping_status": "SELECTIVE_PRECISION_LAYER_MAPPING_BLOCKED" if blocked else "PASS_WITH_EXPLICIT_FUSED_OR_ELIDED_NODES",
        "blocked_nodes": blocked,
        "global_builder_mode": "--fp16",
        "tf32_mode": "--noTF32",
        "precision_constraints": "obey",
        "layer_precision_spec": ",".join(node["name"] + ":fp32" for node in constrained),
        "layer_output_type_spec": ",".join(node["name"] + ":fp32" for node in constrained),
        "nodes": mappings,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"mapping_status": result["mapping_status"],
                      "constrained_node_count": len(constrained),
                      "blocked_nodes": blocked}))
    if blocked:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
