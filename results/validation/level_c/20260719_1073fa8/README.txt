M5 Level C formal evidence

Evidence ID: 20260719_1073fa8
Source commit: 1073fa8be1644dd8562f5704ae31996121883dbb

This evidence uses the explicit Python ONNX Runtime reference and the real C++
edge_ai_defect application. The corpus is 12 validation original images plus
four deterministic runtime-derived BMP images. Image files are deliberately
not included in Git or in this evidence directory.

Python and C++ each ran twice and were byte-identical within their own side.
Both cross-language comparisons passed 16/16 images. Matching is deterministic
maximum bipartite matching by class. Confidence tolerance is 1e-4 and the
bounding-box coordinate tolerance is 0.01 pixel.

This evidence contains no timing, FPS, benchmark, or performance conclusion.
The WSL2 ORT CPU performance baseline has not started. Formal comparison PASS
does not mean that the read-only Level C Gate has passed; the Level C Gate has
not yet been executed.
