# ONNX Runtime C++ SDK

The C++ SDK is a separate dependency from the Python `onnxruntime` package used
for Python reference validation.

| Item | Value |
| --- | --- |
| Dependency | ONNX Runtime C++ SDK |
| Version | 1.23.2 |
| Platform | Linux x64 CPU |
| Archive | `onnxruntime-linux-x64-1.23.2.tgz` |
| Official URL | `https://github.com/microsoft/onnxruntime/releases/download/v1.23.2/onnxruntime-linux-x64-1.23.2.tgz` |
| Downloaded archive SHA256 | `1fa4dcaef22f6f7d5cd81b28c2800414350c10116f5fdd46a2160082551c5f9b` |
| Local SDK path | `third_party/onnxruntime/1.23.2/linux-x64/` |

The SHA256 above records the locally downloaded archive for reproducibility
and file-consistency checks. It was not compared with an independently
published vendor digest and therefore is not an authenticity verification.

The archive and extracted SDK payload are local-only and must not be committed
to Git. This README remains tracked.

## Configure

From the repository root:

```bash
cmake -S . -B build \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DONNXRUNTIME_ROOT="$PWD/third_party/onnxruntime/1.23.2/linux-x64"
```

## Verify the local SDK

```bash
test -f third_party/onnxruntime/1.23.2/linux-x64/include/onnxruntime_c_api.h
test -f third_party/onnxruntime/1.23.2/linux-x64/include/onnxruntime_cxx_api.h
test -e third_party/onnxruntime/1.23.2/linux-x64/lib/libonnxruntime.so
sha256sum third_party/downloads/onnxruntime-linux-x64-1.23.2.tgz
ldd third_party/onnxruntime/1.23.2/linux-x64/lib/libonnxruntime.so
```

The `ldd` output must not contain `not found`.

## M0.3 runtime API smoke

The C++ runtime API smoke test is built at:

```text
build/tests/test_ort_runtime_smoke
```

Run it without relying on `LD_LIBRARY_PATH`:

```bash
env -u LD_LIBRARY_PATH ./build/tests/test_ort_runtime_smoke
```

Verified results:

| Check | Result |
| --- | --- |
| Runtime API version | `1.23.2` |
| Available providers | `CPUExecutionProvider` |
| CPUExecutionProvider | PASS |
| `Ort::Env` lifecycle | PASS |
| `Ort::SessionOptions` lifecycle | PASS |
| Dynamic dependency | `libonnxruntime.so.1` from this project SDK |
| Build RUNPATH | `third_party/onnxruntime/1.23.2/linux-x64/lib` |

Dynamic linking can be inspected with:

```bash
readelf -d build/tests/test_ort_runtime_smoke
ldd build/tests/test_ort_runtime_smoke
readlink -f third_party/onnxruntime/1.23.2/linux-x64/lib/libonnxruntime.so
```

This smoke test validates only the runtime API, version, available Provider,
and basic ORT object lifecycles. It does not create an `Ort::Session`, load a
model, create tensors, or run inference.

## Reinstall

Remove the local archive and payload, recreate their directories, download the
fixed official archive, inspect its structure, record its SHA256, and extract
the single archive root into the versioned SDK directory:

```bash
rm -rf third_party/onnxruntime/1.23.2/linux-x64
rm -f third_party/downloads/onnxruntime-linux-x64-1.23.2.tgz
mkdir -p third_party/downloads third_party/onnxruntime/1.23.2/linux-x64
curl --fail --location --retry 3 --retry-delay 2 \
  --output third_party/downloads/onnxruntime-linux-x64-1.23.2.tgz \
  https://github.com/microsoft/onnxruntime/releases/download/v1.23.2/onnxruntime-linux-x64-1.23.2.tgz
sha256sum third_party/downloads/onnxruntime-linux-x64-1.23.2.tgz
tar -tzf third_party/downloads/onnxruntime-linux-x64-1.23.2.tgz
tar -xzf third_party/downloads/onnxruntime-linux-x64-1.23.2.tgz \
  --strip-components=1 \
  -C third_party/onnxruntime/1.23.2/linux-x64
```
