#!/bin/bash
# Kaldi minimal build for GOP feature extraction (GOPT pipeline)
set -e
exec > /root/kaldi_setup.log 2>&1
echo "=== $(date) start ==="
export DEBIAN_FRONTEND=noninteractive
apt-get install -y -qq build-essential automake autoconf sox gfortran libtool zlib1g-dev libopenblas-dev unzip wget

cd /root
[ -d kaldi ] || git clone --depth 1 https://github.com/kaldi-asr/kaldi.git
cd kaldi/tools
if [ ! -f openfst/lib/libfst.so ]; then
  echo "=== $(date) building tools (openfst) ==="
  make -j2 openfst cub
else
  echo "=== $(date) openfst already installed, skipping tools ==="
fi
df -h / | tail -1

cd ../src
echo "=== $(date) configuring ==="
./configure --shared --mathlib=OPENBLAS --openblas-root=/opt/openblas --use-cuda=no
sed -i 's/ -g / /g' kaldi.mk  # strip debug symbols: 60% smaller objects, disk is tight
make -j2 depend
mkdir -p lib
echo "=== $(date) building src subset ==="
for d in base matrix util feat tree gmm transform fstext hmm lat decoder cudamatrix nnet2 nnet3 chain ivector online2 lm bin featbin fstbin gmmbin latbin nnet3bin ivectorbin online2bin lmbin; do
  echo "--- building $d ($(date +%H:%M))"
  make -j2 -C $d
done
df -h / | tail -1

echo "=== $(date) downloading librispeech chain model ==="
mkdir -p /root/kaldi-models && cd /root/kaldi-models
for f in 0013_librispeech_v1_chain.tar.gz 0013_librispeech_v1_extractor.tar.gz 0013_librispeech_v1_lm.tar.gz; do
  [ -f "$f" ] || wget -q "https://kaldi-asr.org/models/13/$f"
done
ls -lh
echo "=== $(date) ALL DONE ==="
