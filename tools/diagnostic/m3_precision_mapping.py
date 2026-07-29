#!/usr/bin/env python3
"""Create the auditable M3 Backbone/Neck/Detect FP32 precision policy."""

import argparse
import hashlib
import json
import re
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


def stage_for(node_name: str) -> tuple[int, str]:
    match = re.match(r"^/model\.(\d+)/", node_name)
    if not match:
        raise ValueError(f"node is outside YOLO model stages: {node_name}")
    index = int(match.group(1))
    if 0 <= index <= 9:
        return index, "backbone"
    if 10 <= index <= 21:
        return index, "neck"
    if index == 22:
        return index, "detect"
    raise ValueError(f"unexpected YOLO model stage: {node_name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--onnx", type=Path, required=True)
    parser.add_argument("--m2-mapping", type=Path, required=True)
    parser.add_argument("--m2-layer-info", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    nodes = parse_nodes(args.onnx)
    m2 = json.loads(args.m2_mapping.read_text())
    m2_nodes = {node["onnx_node_name"]: node for node in m2["nodes"]}
    layers = json.loads(args.m2_layer_info.read_text()).get("Layers", [])

    selected = []
    excluded = []
    blocked = []
    for node in nodes:
        if not node["name"].startswith("/model."):
            continue
        index, semantic_role = stage_for(node["name"])
        if node["op_type"] == "Constant":
            excluded.append({
                "onnx_node_name": node["name"],
                "onnx_op_type": node["op_type"],
                "semantic_role": semantic_role,
                "exclusion_reason": "constant has no requested execution precision",
            })
            continue

        if semantic_role == "detect":
            # M2 is the frozen complete Detect-head mapping. Reuse its exact
            # membership and identities rather than re-deriving them here.
            if node["name"] not in m2_nodes:
                excluded.append({
                    "onnx_node_name": node["name"],
                    "onnx_op_type": node["op_type"],
                    "semantic_role": semantic_role,
                    "exclusion_reason": "M2 shape-control node retained outside policy",
                })
                continue
            m2_entry = m2_nodes[node["name"]]
            trt_names = m2_entry["tensorrt_network_layer_names"]
            metadata = m2_entry["mapping_evidence"]["trt_layer_metadata_matches"]
            mode = m2_entry["mapping_mode"]
        else:
            matches = [layer for layer in layers
                       if f"[ONNX Layer: {node['name']}]" in str(layer.get("Metadata", ""))]
            if not matches:
                matches = [layer for layer in layers
                           if layer.get("Name") == node["name"]]
            if matches:
                trt_names = [layer.get("Name") for layer in matches]
                metadata = [layer.get("Metadata", "") for layer in matches]
                mode = "detailed_metadata"
            else:
                # TensorRT 10.3 may fuse/elide graph bookkeeping. This is
                # the same explicit parser-identity rule already used by M2.
                trt_names = [node["name"]]
                metadata = []
                mode = "parser_identity_fused_or_elided"

        selected.append({
            "onnx_node": node["name"],
            "onnx_op_type": node["op_type"],
            "onnx_output_tensor": node["outputs"],
            "tensorrt_layer": trt_names,
            "semantic_role": semantic_role,
            "yolo_stage_index": index,
            "requested_precision": "fp32",
            "requested_output_type": "fp32",
            "mapping_mode": mode,
            "mapping_evidence": {
                "source": "frozen M2 mapping and M2 TensorRT 10.3 detailed layer dump",
                "trt_layer_metadata_matches": metadata,
                "m2_exact_mapping_reused": semantic_role == "detect",
            },
        })

    # The policy strings use ONNX parser identities, which are the identities
    # accepted by trtexec --layerPrecisions/--layerOutputTypes. Fused execution
    # names remain recorded above as inspection evidence.
    precision_spec = ",".join(f"{item['onnx_node']}:fp32" for item in selected)
    output_spec = ",".join(f"{item['onnx_node']}:fp32" for item in selected)
    result = {
        "schema_version": 1,
        "artifact_kind": "stage_k_m3_selective_precision_mapping",
        "candidate": "M3_Backbone_Neck_Detect_FP32",
        "source_onnx": str(args.onnx),
        "source_onnx_sha256": sha256(args.onnx),
        "m2_mapping": str(args.m2_mapping),
        "m2_layer_info": str(args.m2_layer_info),
        "semantic_stage_boundary": {
            "backbone": "/model.0 through /model.9",
            "neck": "/model.10 through /model.21",
            "detect": "/model.22",
            "evidence": "frozen YOLOv8 graph module indices and existing M2 Detect mapping",
        },
        "global_builder_policy": ["--fp16", "--noTF32", "--precisionConstraints=obey"],
        "requested_precision": "fp32",
        "requested_output_type": "fp32",
        "constrained_node_count": len(selected),
        "constrained_by_semantic_role": {
            role: sum(item["semantic_role"] == role for item in selected)
            for role in ("backbone", "neck", "detect")
        },
        "excluded_constant_node_count": len(excluded),
        "excluded_nodes": excluded,
        "blocked_nodes": blocked,
        "mapping_status": "PASS" if not blocked else "BLOCKED",
        "layer_precision_spec": precision_spec,
        "layer_output_type_spec": output_spec,
        "nodes": selected,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "mapping_status": result["mapping_status"],
        "constrained_node_count": len(selected),
        "constrained_by_semantic_role": result["constrained_by_semantic_role"],
        "excluded_constant_node_count": len(excluded),
    }))
    if blocked:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
