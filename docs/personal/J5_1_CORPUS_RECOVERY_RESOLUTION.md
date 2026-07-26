# J5.1 Corpus Recovery Resolution

## Status

`RESOLVED`

The historical corpus recovery block is retained as historical record. The
current WSL controlled source has independently passed the frozen benchmark
corpus gate and is ready for the authorized J5.1 Python Reference Campaign.

## Resolution identity

- Historical blocked commit: `e7cf79fd9180ada7ca076dc2dd4467e500282258`
- Benchmark manifest: `tests/data/m5/manifests/benchmark_corpus.json`
- Benchmark manifest SHA256: `235b062cb82166709e2ff800ec71bf92396d5348508281f822ef116d5f0962ab`
- WSL controlled source: `data/yolo/neu_det/images/val`
- Validation environment: WSL x86_64 frozen Python Reference environment
- Historical recovery report: retained unchanged (`docs/personal/J5.1_ENTRY_REPORT.md`)

## WSL benchmark corpus validation

The complete benchmark preparation was rerun from the controlled source with
the frozen `prepare_m5_corpus.py` tool. No download, image generation,
substitution, resize, or JPEG re-encoding was used. No corpus image is
committed to Git.

All 20 entries passed filename order, source/prepared SHA identity and
200×200 dimensions:

| Index | Source / prepared filename | SHA256 |
|---:|---|---|
| 0000 | `crazing_51.jpg` / `0000_crazing_51.jpg` | `185daa31428cf2467d48f9f57ff582575d07a796cd26d77f3e05537bae681503` |
| 0001 | `crazing_10.jpg` / `0001_crazing_10.jpg` | `522352a6c3532d45a64184b7b1435a74e8cdb732ebdc8e062ced67fa737cf63c` |
| 0002 | `inclusion_18.jpg` / `0002_inclusion_18.jpg` | `c1c54814ecaf2bf4f6d84aaf5c744fb648dc3c8323c3b0cfe1bd9f55df20788b` |
| 0003 | `inclusion_217.jpg` / `0003_inclusion_217.jpg` | `e40821c51a341286572663cbba1159e7efe8a7cd729c763a5c439d851e6a9c77` |
| 0004 | `patches_156.jpg` / `0004_patches_156.jpg` | `9961f0ffde85a40516f54262b3fa74eb35cee24fc87a54d4fe8f07b7e7fb2ec2` |
| 0005 | `patches_211.jpg` / `0005_patches_211.jpg` | `f988631bac3b31eac7be7a1f56e118d14d3327989ce4b454370761c5c8700305` |
| 0006 | `pitted_surface_224.jpg` / `0006_pitted_surface_224.jpg` | `419e1d0d40ce7c53fcce40b55f4b8091d4573881d2315969d74318df493a0e80` |
| 0007 | `pitted_surface_231.jpg` / `0007_pitted_surface_231.jpg` | `0bfa310238545597ac7a48495a85ae1a945d2f6f8e4fa470d1bce5f4648c931c` |
| 0008 | `rolled-in_scale_146.jpg` / `0008_rolled-in_scale_146.jpg` | `4b76ee7c33602b95115a2acec07b4cd74cab87eeb2cdc2a602534646cbed047b` |
| 0009 | `rolled-in_scale_262.jpg` / `0009_rolled-in_scale_262.jpg` | `67cab4d93752e5def8a7d34b72504c1ecacadc673f252d4d719b716aeda0c083` |
| 0010 | `scratches_126.jpg` / `0010_scratches_126.jpg` | `fd1f86fe4349e991e98e1b00c1b1aa94088669822cdb30a5c0dfffa5782134c3` |
| 0011 | `scratches_246.jpg` / `0011_scratches_246.jpg` | `06811a835826c47ad78e91e90cb758f6334f348d21765375b2ce9146be1309b4` |
| 0012 | `crazing_102.jpg` / `0012_crazing_102.jpg` | `b4e276eb131f61b44084d0c06640b00cbaecbffb48d3a8f3120d7aaa5cc84a53` |
| 0013 | `inclusion_135.jpg` / `0013_inclusion_135.jpg` | `96a0fd79d5c8d6eab03b09e2331e258b931fd1b4523668b5b49f8ab69075ce67` |
| 0014 | `patches_164.jpg` / `0014_patches_164.jpg` | `87c1b46a01c796c71030ee72ca51ae732fb2e4e8a39117e483e5b42fa55a9b8e` |
| 0015 | `pitted_surface_225.jpg` / `0015_pitted_surface_225.jpg` | `23be66132f661ba432b06ba402734cbe12d05d5eca0bebed90b99d9f15cec92f` |
| 0016 | `rolled-in_scale_133.jpg` / `0016_rolled-in_scale_133.jpg` | `f66ffd8a184bc11ec947078c3c206fac71b1118683deb5e8b3731811a0ae2ec3` |
| 0017 | `scratches_154.jpg` / `0017_scratches_154.jpg` | `3e96489cf25f15a08c3dcebbec97afabdfb58468847e51a70d880a35a104b72c` |
| 0018 | `inclusion_16.jpg` / `0018_inclusion_16.jpg` | `1ff85f67c5d902bf00a37895e4ea86ca2a49bb1c452fa9fc44d0431f154a3940` |
| 0019 | `scratches_221.jpg` / `0019_scratches_221.jpg` | `e65d748792cd1010f663588aec6437acad9a26c92a30ea263b67febed363b27b` |

Result: `20/20 PASS`; prepared filenames are exactly `0000`–`0019`, all
images are 200×200, and the prepared manifest records the frozen benchmark
manifest SHA above. The Jetson local corpus was also verified 20/20 in the
recovery activity; that copy remains reserved for J5.2 and later Jetson work.

## Campaign state

- J5.1 Python Reference: `READY`
- J5.2: `NOT_STARTED`
- Jetson formal Python Reference: not run
- Benchmark/performance/telemetry/TensorRT: not run
