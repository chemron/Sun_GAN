#!/bin/bash

#SBATCH --job-name=Data_collection

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

# >>> conda initialize >>> SPECIFIC TO MONARCH
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/usr/local/anaconda/2020.07-python3.8-gcc8/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/usr/local/anaconda/2020.07-python3.8-gcc8/etc/profile.d/conda.sh" ]; then
        . "/usr/local/anaconda/2020.07-python3.8-gcc8/etc/profile.d/conda.sh"
    else
        export PATH="/usr/local/anaconda/2020.07-python3.8-gcc8/bin:$PATH"
    fi
fi
unset __conda_setup
conda config --add pkgs_dirs /home/csmi0005/Mona0028/csmi0005/conda/pkgs
# <<< conda initialize <<<#

# activate conda environment
conda activate ./Data_env


echo "Getting STEREO-A positional data"
# get positional data for STEREO-A
python Data_collection/get_stereo_phase_times.py


echo "Getting AIA, HMI, EUVI fits data"
# get SDO (AIA/HMI) and STEREO (EUVI) data
python Data_collection/get_SDO_STEREO_data.py \
        --instruments 'AIA' 'HMI' 'EUVI' \
        --start '2010-06-01 00:00:00' \
        --end '2010-06-07 00:00:00' \
        --cadence 12 \
        --path  './Data/' \
        --email "camerontasmith@gmail.com"

echo "Getting farside siesmic fits data"
# get phase maps (seismic data)
python Data_collection/get_seismic_data.py \
        --start '2010-06-01 00:00:00' \
        --end '2010-06-07 00:00:00' \
