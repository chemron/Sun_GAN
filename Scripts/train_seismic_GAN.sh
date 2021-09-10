#!/bin/bash

#SBATCH --job-name=train_seismic

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
    --model_name "Seismic_GAN_1" \
    --display_iter 5 \
    --max_iter 20 \
    --batch_size 1 \
    --tol $((9*24)) \
    --input "phase_map.np_path_normal" \
    --output "euvi.UV_GAN_1_iter_0000020_path" \
    --connector "phase_map.id" "euvi.phase_map_id" \
# input: sql data name (table.column)
# output: sql data name (table.column)
# connector: the connection between the input and output
# tol: the time difference between input and output data in hours (must be large
# for seismic gan, as most euvi data is not directly from farside - see thesis)
