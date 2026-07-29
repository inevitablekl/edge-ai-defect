# D062 Parameter Semantic Verification

Source: `trtexec_help.txt`, captured from TensorRT `v100300`.

| Option | Observed TensorRT 10.3 semantic | Contract decision |
|---|---|---|
| `--onnx=<file>` | Selects an ONNX model input | Use frozen ONNX path in K2 only; not executed in D062 |
| `--saveEngine=<file>` | Saves serialized Engine | Use exact local Engine path in K2 only; not executed in D062 |
| `--loadEngine=<file>` | Loads serialized Engine | Use only for post-build inspection/load smoke |
| `--fp16` | Enables FP16 in addition to FP32 | Enabled; mixed precision claim only |
| `--memPoolSize=poolspec` | Sets named memory-pool constraints; supports B/G/K/M base-2 suffixes; default unit MiB | Freeze `workspace:4096M` |
| `--workspace` | Not present in observed help | Forbidden; do not use TensorRT 8.x syntax |
| `--minShapes` | Dynamic profile minimum shape; all min/opt/max required when used | Omit: frozen ONNX contract is static |
| `--optShapes` | Dynamic profile optimization shape; alone expands min/max to opt | Omit: frozen ONNX contract is static |
| `--maxShapes` | Dynamic profile maximum shape | Omit: frozen ONNX contract is static |
| `--inputIOFormats` | Input tensor types/formats; default `fp32:chw` | Freeze `fp32:chw` |
| `--outputIOFormats` | Output tensor types/formats; default `fp32:chw` | Freeze `fp32:chw` |
| `--skipInference` | Exits after Engine build and skips inference measurement | Include in offline build |
| `--int8` | Enables INT8 in addition to FP32 | Omit; INT8 disabled |
| `--useDLACore` | Selects a DLA core; default none | Omit; DLA disabled |
| `--buildDLAStandalone` | Builds DLA standalone loadable and implies skip inference | Omit; DLA disabled |
| `--saveEngine`/`--loadEngine` | Separate serialization and loading operations | Build and independent load smoke remain separate |

The help also confirms `--minShapes`, `--optShapes`, and `--maxShapes` are
profile controls. They are not included in the static-shape contract.
