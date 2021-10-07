#!/bin/bash

#SBATCH --job-name=stereo_50

# Request CPU resource for a serial job
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

# Request for GPU,
#SBATCH --partition=gpu
# SBATCH --gres=gpu:P100:1
#SBATCH --gres=gpu:K80:1


# Memory usage (MB)
#SBATCH --mem=7G

# Set your minimum acceptable walltime, format: day-hours:minutes:seconds
#SBATCH --time=12:00:00

#SBATCH --mail-user=csmi0005@student.monash.edu
#SBATCH --mail-type=FAIL

# Command to run a gpu job

module load anaconda/5.1.0-Python3.6-gcc5
module load cudnn/7.6.5-cuda10.1
module load tensorflow/2.3.0

python Training/test.py \
    --model_name 'UV_GAN_1' \
    --input_data 'aia.np_path_normal' \
    --test_on_all \
    --display_iter 50000 \
    --start_iter 0 \
    --max_iter 500000

python Training/test.py \
    --model_name 'UV_GAN_1' \
    --input_data 'euvi.np_path_normal' \
    --test_on_all \
    --display_iter 50000 \
    --start_iter 0 \
    --max_iter 500000


# input data: sql data name (table.column)
# test on all: either test on all the input data, or just the test data (i.e
# data from october or november)

# apply mask to outputs
python Data_processing/apply_mask.py \
    --data "euvi.UV_GAN_1_iter_500000_path"

# data: data to apply mask to ([sql table].[column])
