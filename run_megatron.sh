#!/bin/bash
#SBATCH --job-name=run_megatron
#SBATCH --output=run_megatron_%j.out
##SBATCH --error=run_megatron_%j.err
#SBATCH -t 00:30:00
##SBATCH -p mi2104x
#SBATCH -p mi3008x
#SBATCH -q alloc_diwu_05142024_06302025

cd $SLURM_SUBMIT_DIR
CONTAINER_HOME=$SLURM_SUBMIT_DIR
SIF_FILE=megatron-container.sif

export TEE_OUTPUT=1
export MBS=2
export BS=64
export TP=8
export TE_FP8=0
export SEQ_LENGTH=4096
export ENABLE_PROFILING=1
export TOTAL_ITERS=2

rocprof --list-basic

echo "RUNANDTIME_START $(date +%s)"
time srun apptainer exec --rocm \
        ${CONTAINER_HOME}/${SIF_FILE} \
        bash $SLURM_SUBMIT_DIR/examples/llama/train_llama3.sh
echo "RUNANDTIME_STOP $(date +%s)"


