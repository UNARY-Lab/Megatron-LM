#!/bin/bash
#SBATCH --job-name=build_megatron
#SBATCH --output=build_megatron_%j.out
#SBATCH --time=08:00:00
#SBATCH --partition=ghx4
#SBATCH --account=bcrc-dtai-gh
#SBATCH --gpus-per-node=4

cd ${SLURM_SUBMIT_DIR} || { echo "Directory not found"; exit 1; }
apptainer build --force megatron-container.sif nemo.def
