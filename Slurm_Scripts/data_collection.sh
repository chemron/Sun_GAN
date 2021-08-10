#!/bin/bash

#SBATCH --job-name=data_collection

# Request CPU resource for a serial job
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
# SBATCH --partition=short,comp

# Memory usage (MB)
#SBATCH --mem=20G

# Set your minimum acceptable walltime, format: day-hours:minutes:seconds
#SBATCH --time=03:00:00

#SBATCH --mail-user=csmi0005@student.monash.edu
#SBATCH --mail-type=FAIL

conda activate ./data_nv
cd Honours/data_collection

python get_data.py \
        --instruments 'HMI' \
        --series 'hmi.m_45s' \
        --segment 'magnetogram' \
        --start '2019-10-27 00:00:00' \
        --end '2020-01-01 00:00:00' \
        --cadence 12 \
        --path  './DATA/' \
        --wavelength 0 \
        --email "camerontasmith@gmail.com"
