#!/bin/bash

#SBATCH --job-name=train_P100

# Request CPU resource for a serial job
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

# Request for GPU,
#SBATCH --partition=gpu
#SBATCH --gres=gpu:P100:1
# SBATCH --gres=gpu:K80:1

# Memory usage (MB)
#SBATCH --mem=10G

# Set your minimum acceptable walltime, format: day-hours:minutes:seconds
#SBATCH --time=90:00:00
# SBATCH --time=00:00:20

#SBATCH --mail-user=csmi0005@student.monash.edu
#SBATCH --mail-type=FAIL

module load anaconda/5.1.0-Python3.6-gcc5
module load cudnn/7.6.5-cuda10.1
module load tensorflow/2.3.0

python Training/train.py \
    --model_name "P100_UV_GAN_1" \
    --display_iter 5 \
    --max_iter 20 \
    --batch_size 1 \
    --tol $((5*24)) \
    --input "aia.np_path_normal" \
    --output "hmi.np_path_normal" \
    --connector "aia.id" "hmi.aia_id" \
