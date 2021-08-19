# Sun_GAN
See [my honours thesis](https://github.com/chemron/honours_thesis/blob/master/thesis.pdf) for a full description of the system. 


## Environments
### Data processing
A conda environment used for all data processing tasks. A similar conda environment can be constructed from `requirements.txt` or using the command:
`conda create --prefix ./data_env`
`conda activate ./data_env/`
`conda config --add channels conda-forge`
`conda install sunpy=3.0.1 astropy=4.3.post1 numpy=1.21.1 drms=0.6.2 requests=2.26.0 scikit-image=0.18.2 imageio=2.9.0 pandas=1.3.1 pillow=8.3.1 opencv=4.5.2 matplotlib=3.4.2`


### Training/Testing
Training and testing of each GAN was done in a [Monarch](https://docs.monarch.erc.monash.edu/) environment created using the following commands:

`module load anaconda/5.1.0-Python3.6-gcc5`
`module load cudnn/7.6.5-cuda10.1`
`module load tensorflow/2.3.0`

## Pipeline: Data Preparation
The pipeline for downloading and preparing the data used throughout this project.
### Data collection
Download fits data (SDO AIA/HMI, STEREO EUVI and phase maps): `./Scripts/data_collection.sh` or `sbatch ./Scripts/data_collection.sh` on Monarch.
The STEREO data is downloaded such that it is synchronised with the phase maps.

### Data processing
1. Convert fits data into local numpy arrays (.npy), and get percentiles of the data: `./Scripts/fits_to_np.sh` or `sbatch ./Scripts/fits_to_np.sh` on Monarch.
2. 

## Pipeline: UV-GAN
The pipeline for generating magnetograms from EUV 304 Angstrom full-disk solar images.

