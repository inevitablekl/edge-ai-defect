# K1-R3 Dynamic Linker Diagnosis

```text
K1 BLOCKED
D062 NOT_AUTHORIZED
```

This is a read-only diagnosis of the installed
`libnvdla_compiler.so` not being resolved as a dependency of
`libnvinfer.so.10`. The loader configuration contains the NVIDIA library
directory, but the loader cache lacks `libnvdla_compiler.so`; the cache
timestamp predates package installation. ELF dependency metadata and package
ownership are consistent.

Classification: `DYNAMIC_LINKER_CONFIGURATION_ERROR` (Category B), with the
specific observed condition `CACHE_MISSING_LIBNV_DLA_COMPILER`.

No remediation was executed.
