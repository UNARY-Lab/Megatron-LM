#!/bin/bash
#SBATCH --job-name=build_megatron
#SBATCH --output=sbatch_output/build_megatron_%j.out
#SBATCH -t 08:00:00
#SBATCH -p mi2104x
#SBATCH -q alloc_diwu_05142024_06302025

cd ${SLURM_SUBMIT_DIR} || { echo "Directory not found"; exit 1; }
# apptainer build --tmpdir $MYHOME/.apptainer --force nemo-container.sif nemo.def

### gfx942
# apptainer pull megatron-container.sif docker://rocm/megatron-lm:24.12-dev

### gfx90a
# apptainer build --tmpdir $MYHOME/.apptainer --force megatron-container-gfx90a.sif megatron.def
rm -rf /tmp/*
rm -rf /tmp/.*
du -d0 -h /tmp
df -h /tmp
mkdir -p /tmp/mkurzynski/.apptainer
export APPTAINER_TMPDIR="/tmp"
export TMPDIR="/tmp"
apptainer build --force megatron-container-gfx90a.sif megatron.def
