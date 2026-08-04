# Paper Phase 2 Literature Requirements v1.0

## 1. Policy

This file defines evidence needs; it is not a bibliography. No author, title,
DOI, journal, or publication fact is created here. Every future reference must
be found, opened, read, and verified before it enters the article.

Date ranges below are search priorities, not exclusion rules for necessary
foundational work. Current planning date: `2026-08-04`.

## 2. Requirement Register

| literature_requirement_id | section | question_to_support | preferred_source_type | date_range | search_terms_cn | search_terms_en | minimum_quality | citation_needed | status |
|---|---|---|---|---|---|---|---|---|---|
| L1 | 0;1.1 | Why are industrial surface-defect detection and edge deployment relevant, and what deployment constraints are commonly reported? | Peer-reviewed review plus representative primary studies | 2020-2026; allow earlier foundational work | 工业表面缺陷检测;边缘部署;实时视觉检测;钢材表面缺陷 | industrial surface defect detection;edge deployment;real-time visual inspection;steel surface defects | Indexed peer-reviewed journal/conference;methods and test conditions available | YES | TODO_SEARCH_AND_VERIFY |
| L2 | 0;1.1;3.1 | How are YOLOv8 and NEU-DET used/evaluated in related defect-detection work, and what are common limitations? | Primary model documentation plus peer-reviewed application studies | 2022-2026 for YOLOv8;foundational NEU-DET source allowed | YOLOv8 缺陷检测;NEU-DET;钢材表面缺陷数据集 | YOLOv8 defect detection;NEU-DET dataset;steel surface defect dataset | Prefer original dataset/model authority and reproducible peer-reviewed studies;avoid unsourced tutorials | YES | TODO_SEARCH_AND_VERIFY |
| L3 | 0;1.2;2.2;3.1 | What principles and deployment trade-offs govern TensorRT FP16 and INT8 PTQ? | NVIDIA/TensorRT official documentation plus peer-reviewed quantization/deployment studies | Version-matched official docs;2019-2026 research | TensorRT FP16;INT8 后训练量化;校准;混合精度推理 | TensorRT FP16;INT8 post-training quantization;calibration;mixed-precision inference | Primary official documentation for API behavior;peer-reviewed source for general method claims | YES | TODO_SEARCH_AND_VERIFY |
| L4 | 0;2.2;4.2 | What work analyzes GPU preprocessing, fused image transforms, and end-to-end inference data paths? | Peer-reviewed systems/deployment papers and official implementation documentation | 2018-2026;prioritize 2024-2026 | GPU 图像预处理;CUDA 预处理;融合预处理;推理数据路径 | GPU image preprocessing;CUDA preprocessing;fused preprocessing;inference data path | Must define measurement boundary and hardware/workload;prefer released code/data | YES | TODO_SEARCH_AND_VERIFY |
| L5 | 0;2.3;4.3 | How do pageable and pinned host memory affect H2D transfer and pipeline behavior, and under what conditions? | CUDA official programming/best-practices documentation plus peer-reviewed systems studies | Current version-matched docs;foundational memory studies allowed;2020-2026 applications | 可分页内存;锁页内存;主机到设备传输;CUDA 数据传输 | pageable host memory;pinned host memory;host-to-device transfer;CUDA data transfer | Primary CUDA authority for semantics;measured studies must disclose sizes/synchronization/platform | YES | TODO_SEARCH_AND_VERIFY |
| L6 | 0;3.3;4.4 | How should inference latency, end-to-end latency, throughput, FPS, and tail latency be defined and reported? | Benchmark standards/guidelines and peer-reviewed systems methodology | 2018-2026;foundational percentile references allowed | 推理延迟;端到端延迟;吞吐率;帧率;尾延迟;百分位数 | inference latency;end-to-end latency;throughput;frame rate;tail latency;percentile | Definitions must state start/end boundary, aggregation, and percentile method | YES | TODO_SEARCH_AND_VERIFY |
| L7 | 0;4.4 | What are the latest edge-vision and industrial-detection findings that frame the article's current relevance? | Recent peer-reviewed primary studies/reviews | 2024-2026 | 近年 边缘视觉;工业缺陷检测;Jetson 实时推理;部署优化 | recent edge vision;industrial defect detection;Jetson real-time inference;deployment optimization | Published/accepted peer-reviewed work;avoid metadata-only citation;read full text | YES | TODO_SEARCH_AND_VERIFY |
| L8 | 0;all as relevant | Which related topics, terminology, and presentation patterns appear in the target journal during the latest 3 years? | Official target-journal article pages/PDFs | 2023-08-04 to 2026-08-04 | 合肥工业大学学报 自然科学版;机器视觉;缺陷检测;边缘计算;深度学习部署 | Journal of Hefei University of Technology Natural Science;machine vision;defect detection;edge computing;deep learning deployment | Official journal source;article must be directly relevant and read before citation | YES | TODO_SEARCH_AND_VERIFY |
| L9 | 1.2;2;3 | Which NVIDIA/CUDA/TensorRT definitions and API behaviors require primary technical authority? | NVIDIA, CUDA, and TensorRT official documentation | Version-matched where possible: CUDA 12.6/TensorRT 10.3;current docs noted separately | NVIDIA Jetson;CUDA 内存;TensorRT INT8;执行上下文;同步 | NVIDIA Jetson;CUDA memory;TensorRT INT8;execution context;synchronization | Official vendor documentation only for API/version behavior;record access date/version | YES | TODO_OFFICIAL_DOC_REVIEW |

## 3. Search and Selection Rules

- Meet the journal's general expectation of at least 8 references with real,
  read sources; the final count should be driven by claim coverage rather than
  padding.
- Include recent domestic and international work and relevant target-journal
  work; prioritize 2024-2026 literature for the introduction's recent-work
  requirement.
- Prefer original papers, datasets, standards, and official documentation over
  secondary summaries.
- Record title, authors, venue, year, DOI/URL, source type, section/claim served,
  and verification status only after opening the source.
- Use sequential numeric citation order in the eventual article.
- A source may satisfy multiple literature requirements only when its content
  directly supports each mapped question.
- Do not cite a source based only on search-result snippets, titles, or an
  unverified DOI.

## 4. Coverage Gate Before Drafting

Drafting may begin only when:

- L1-L6 each have at least one verified high-quality source;
- L7 contains verified 2024-2026 work;
- L8 contains verified target-journal work from the defined three-year window,
  or a documented `NO_RELEVANT_ITEM_FOUND` search record;
- L9 contains version-aware official documentation;
- every external factual assertion in the introduction has a source mapping;
- no placeholder has been silently converted into a reference entry.
