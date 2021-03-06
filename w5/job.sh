#!/usr/bin/env bash
#SBATCH --job-name w5
#SBATCH --ntasks 4
#SBATCH --mem 16G
#SBATCH --partition mhigh
#SBATCH --qos masterhigh
#SBATCH --gres gpu:1
#SBATCH --chdir /home/grupo06/
#SBATCH --output logs/%x_%u_%j.out

source venv/bin/activate
python m3-project/w5/train.py ${SLURM_JOB_ID}