#!/bin/bash

#SBATCH --job-name=flux

# Request CPU resource for a serial job
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
# SBATCH --partition=short,comp

# Memory usage (MB)
#SBATCH --mem=30G

# Set your minimum acceptable walltime, format: day-hours:minutes:seconds
#SBATCH --time=30:00:00

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

python Data_processing/get_unsigned_flux.py \
    --data 'aia.UV_GAN_1_iter_0000020_path' 'euvi.UV_GAN_1_iter_0000020_path' \
        'hmi.np_path_normal' 'phase_map.Seismic_GAN_1_iter_0000020_path'
