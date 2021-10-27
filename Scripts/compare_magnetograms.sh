#!/bin/bash

#SBATCH --job-name=compare_mag

# Request CPU resource for a serial job
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
# SBATCH --partition=short,comp

# Memory usage (MB)
#SBATCH --mem=20G

# Set your minimum acceptable walltime, format: day-hours:minutes:seconds
#SBATCH --time=40:00:00

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

# iters=("0050000" "0100000" "0150000" "0200000" "0250000" "0300000" "0350000" "0400000" "0450000" "0500000")
echo "Comparing UV magnetograms"
iters=("0300000" "0350000" "0450000", "0500000")
UV_GAN_model='UV_GAN_1'

for iter in ${iters[@]}
do
    python Plotting/compare_magnetograms.py \
        --UV_GAN_iter $iter \
        --UV_GAN_model $UV_GAN_model \

done

echo "Comparing Seismic Magnetograms"
iters=()
Seismic_GAN_model='Seismic_GAN_1'
for iter in ${iters[@]}
do
    python Plotting/compare_magnetograms.py \
        --Seismic_GAN_iter $iter \
        --Seismic_GAN_model $Seismic_GAN_model
done
