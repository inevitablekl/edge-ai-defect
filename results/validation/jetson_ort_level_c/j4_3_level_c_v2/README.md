# J4.3 Level C robustness — PASS

Formal Level C executed on the recovered frozen 16-image corpus with the
frozen ONNX model and CPU-only ONNX Runtime. Both independent application
processes produced byte-identical payloads. The frozen class-aware maximum
bipartite matching comparator passed all 16 images.

The first v2 RuntimeConfig application attempt is retained in the local
attempt records: the current ResultSink rejects RunMetadata schema 2. The
formal application run therefore used the existing v1-compatible application
entry with the same frozen model, postprocess values, CPU-only ORT defaults
(sequential, graph optimization all, intra/inter threads 1), and CPU 5
affinity. No source, model, ONNX, corpus, manifest, or golden was changed.

The historical strict Level B CTest failure remains visible and is the D048
accepted cross-architecture numerical limitation. J4.4 was not started.
