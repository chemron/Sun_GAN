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

# load anaconda module on monarch
module load 

# activate conda environmnt
conda activate ./data_env

# get SDO data
python data_collection/get_SDO_data.py \
        --instruments 'AIA' 'HMI' \
        --start '2010-06-01 00:00:00' \
        --end '2010-06-07 00:00:00' \

# get positional data for STEREO-A
python get_stereo_phase_times

# get STEREO DATA that overlaps with phase maps
python data_collection/get_STEREO_data.py \
        --start '2010-06-01 00:00:00' \
        --end '2010-06-07 00:00:00' \

# get phase maps (seismic data)
python data_collection/get_seismic_data.py \
        --start '2010-06-01 00:00:00' \
        --end '2010-06-07 00:00:00' \
