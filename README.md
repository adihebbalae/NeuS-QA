<div align="center">

# NeuS-QA: Grounding Long-Form Video Understanding in Temporal Logic and Neuro-Symbolic Reasoning 

[![arXiv](https://img.shields.io/badge/arXiv-2509.18041-b31b1b.svg)](https://arxiv.org/abs/2509.18041) [![Paper](https://img.shields.io/badge/Paper-pdf-green.svg)](https://arxiv.org/pdf/2509.18041) [![Website](https://img.shields.io/badge/ProjectWebpage-neus--qa-orange.svg)](https://utaustin-swarmlab.github.io/NeuS-QA/) [![GitHub](https://img.shields.io/badge/Code-Source--Code-blue.svg)](https://github.com/UTAustin-SwarmLab/NeuS-QA)
</div>

### Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Citation](#citation)

<a name="overview"></a>
## :mega: Overview

<b>TL;DR: NeuS-QA is a training-free, plug-and-play VQA pipeline that improves long video question answering by translating questions into temporal logic and using model checking to identify only logic-verified video segments.</b>

> While vision-language models (VLMs) excel at tasks involving single images or short videos, they still struggle with Long Video Question Answering (LVQA) due to its demand for complex multi-step temporal reasoning. Vanilla approaches, which simply sample frames uniformly and feed them to a VLM along with the question, incur significant token overhead. This forces aggressive downsampling of long videos, causing models to miss fine-grained visual structure, subtle event transitions, and key temporal cues. Recent works attempt to overcome these limitations through heuristic approaches; however, they lack explicit mechanisms for encoding temporal relationships and fail to provide any formal guarantees that the sampled context actually encodes the compositional or causal logic required by the question. To address these foundational gaps, we introduce NeuS-QA, a training-free, plug-and-play neuro-symbolic pipeline for LVQA. NeuS-QA first translates a natural language question into a logic specification that models the temporal relationship between frame-level events. Next, we construct a video automaton to model the video's frame-by-frame event progression, and finally employ model checking to compare the automaton against the specification to identify all video segments that satisfy the question's logical requirements. Only these logic-verified segments are submitted to the VLM, thus improving interpretability, reducing hallucinations, and enabling compositional reasoning without modifying or fine-tuning the model. Experiments on the LongVideoBench and CinePile LVQA benchmarks show that NeuS-QA significantly improves performance by over 10%, particularly on questions involving event ordering, causality, and multi-step reasoning.

<a name="installation"></a>
## :hammer: Installation
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
./build_dependency.sh
```

### LongVideoBench Setup
1. Download the LongVideoBench dataset from HuggingFace:
```bash
git lfs install
git clone https://huggingface.co/datasets/longvideobench/LongVideoBench
```
2. Burn subtitles into the videos using the provided script (see `scripts/burn_subtitles.py` for path configurations):
```bash
python3 scripts/burn_subtitles.py
```

<a name="usage"></a>
## :tv: Usage
To run NeuS-QA on either LongVideoBench or CinePile, run:
```bash
python3 evaluate.py --current_split 1 --total_splits 4 --device 0
```

If you wish to parallelize the task across multiple GPUs, you can use the `--current_split` and `--total_splits` arguments. 
- `--total_splits`: The total number of chunks to divide the dataset into (e.g., matching your number of GPUs).
- `--current_split`: The specific chunk index (1-indexed) to process in the current run.
- `--device`: The GPU device ID to use for the execution.
The above example runs the first of four splits on GPU 0:

To run the actual VQA, you can either:
- Modify `evaluate.py` to enable the `vqa` function call at the end of the script.
- Run via `lmms-eval` by first preparing the dataset with `scripts/prepare_lmms.py` and then running lmms-eval:
```bash
python3 scripts/prepare_lmms.py
bash vendors/lmms-eval/run_lmms.sh
```

<a name="citation"></a>
## :clipboard: Citation

```bibtex
@inproceedings{shah2025neus,
  title={NeuS-QA: Grounding Long-Form Video Understanding in Temporal Logic and Neuro-Symbolic Reasoning},
  author={Shah, Sahil and Sharan, SP and Goel, Harsh and Choi, Minkyu and Munir, Mustafa and Pasula, Manvik and Marculescu, Radu and Chinchali, Sandeep},
  booktitle={Proceedings of the AAAI Conference on Artificial Intelligence},
  year={2026}
}
```
