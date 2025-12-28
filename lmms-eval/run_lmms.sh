#!/bin/bash

export CUDA_DEVICE_ORDER="PCI_BUS_ID"
export CUDA_VISIBLE_DEVICES="7"
export DECORD_EOF_RETRY_MAX=20480

mkdir ./logs/mylog

# Qwen2.5 VL
python3 -m accelerate.commands.launch \
    --num_processes=8 \
    -m lmms_eval \
    --model openai_compatible \
    --model_args model_version=gpt-4o \
    --batch_size 1 \
    --verbosity=DEBUG \
    --tasks longvideobench_val_v \
    --log_samples \
    --output_path ./logs/mylog
