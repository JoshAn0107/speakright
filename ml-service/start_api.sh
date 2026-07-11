#!/bin/bash
export SPEAKRIGHT_MODEL=/root/speakright-ml/checkpoints/wav2vec2_finetuned_ctc
export SPEAKRIGHT_DEVICE=cpu
cd /root/speakright-ml
exec /root/mlenv/bin/uvicorn src.api.server:app --host 0.0.0.0 --port 8002 --workers 1
