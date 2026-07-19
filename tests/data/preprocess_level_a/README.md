# Preprocess Level A Assets

These deterministic assets validate the production C++ `Preprocessor` against
a Python OpenCV 4.10.0 reference without image decoding. Inputs are headerless
uint8 HWC BGR bytes. Golden tensors are headerless little-endian float32 NCHW.

Regenerate from the repository root:

```bash
.venv/bin/python tools/validation/generate_preprocess_level_a.py \
  --output-root tests/data/preprocess_level_a
```

Verify tracked asset hashes from this directory with `sha256sum -c SHA256SUMS`.
