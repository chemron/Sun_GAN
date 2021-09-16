#!/bin/bash

#SBATCH --job-name=data_processing

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


for Instrument in AIA HMI EUVI
do
    echo "Converting ${Instrument} data to numpy arrays"
    python Data_processing/fits_to_np.py \
            --data $Instrument
done

echo "Re-projecting seismic maps"
python Data_processing/reproject.py

echo "normalising EUV data"
python Data_processing/normalise_EUV_data.py

echo "normalising HMI data"
python Data_processing/normalise_mag_data.py

echo "normalising seismic data"
python Data_processing/normalise_seismic_data.py

echo "creating database"
python Data_processing/create_database.py
