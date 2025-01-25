#!/bin/bash
#SBATCH --account=bcrc-dtai-gh
#SBATCH --job-name=run_megatron
#SBATCH --output=run_megatron_%j.out
#SBATCH --partition=ghx4
##SBATCH --reservation=affinity1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=4
#SBATCH --mem=748GB
#SBATCH --time=02:00:00


cd $SLURM_SUBMIT_DIR
CONTAINER_HOME=$SLURM_SUBMIT_DIR
SIF_FILE=megatron-container.sif

export TEE_OUTPUT=1
export MBS=2
export BS=64
export MODEL_SIZE=13
export TP=4
export TE_FP8=0
export SEQ_LENGTH=4096

echo "RUNANDTIME_START $(date +%s)"
time srun apptainer exec --nv \
        ${CONTAINER_HOME}/${SIF_FILE} \
        bash $SLURM_SUBMIT_DIR/examples/llama/train_llama3.sh
echo "RUNANDTIME_STOP $(date +%s)"


