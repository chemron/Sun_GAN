# Sun_GAN
See [my honours thesis](https://github.com/chemron/honours_thesis/blob/master/thesis.pdf) for a full description of the system. 


## Environments
### Data processing
A conda environment used for all data processing tasks. A similar conda
environment can be constructed from `requirements.txt` or using the command:  
`conda create --prefix ./Data_env`  
`conda activate ./Data_env/`  
`conda config --add channels conda-forge`  
`conda install sunpy=3.0.1 astropy=4.3.post1 numpy=1.21.1 drms=0.6.2
requests=2.26.0 scikit-image=0.18.2 imageio=2.9.0 pandas=1.3.1 pillow=8.3.1
opencv=4.5.2 matplotlib=3.4.2`  


### Training/Testing
Training and testing of each GAN was done in a
[Monarch](https://docs.monarch.erc.monash.edu/) environment created using the
following commands:  

`module load anaconda/5.1.0-Python3.6-gcc5`  
`module load cudnn/7.6.5-cuda10.1`  
`module load tensorflow/2.3.0`  

## Pipeline: Data Preparation
The pipeline for downloading and preparing the data used throughout this project.
### Data collection
Download fits data (SDO AIA/HMI, STEREO EUVI and phase maps):  
  `./Scripts/Data_collection.sh` or  
  `sbatch ./Scripts/Data_collection.sh` (Monarch).  
The STEREO data is downloaded such that it is synchronised with the phase maps.

### Data processing
The processing pipleine consists of
1. Converting fits data into local numpy arrays (.npy), and getting percentiles of the
   data
2. Normalising the data SDO and STEREO (remove outliers, change saturation and
   make EUV data consistant - see
   [thesis](https://github.com/chemron/honours_thesis/blob/master/thesis.pdf))
3. Creating a database (`image.db`) that maps the connections between the different
   data types
4. Reprojecting the seismic maps (phase maps) from a Carrington Heliographic
   projection to a Helioprojective-cartesian projection.

This can be done by running the data processing pipeline file as follows:  
`./Scripts/data_normalisation.sh` or   
`sbatch ./Scripts/data_normalisation.sh` (Monarch).  

## Pipeline: UV-GAN
The pipeline for generating magnetograms from EUV 304 Angstrom full-disk solar
images.
1. Train model on SDO AIA EUV images and SDO HMI magnetograms:  
   `./Scripts/train_UV_GAN.sh` or   
   `sbatch ./Scripts/train_UV_GAN.sh` (Monarch). See `train_UV_GAN.sh` for
   additional settings such as # itterations, model name etc.
2. Evaluate model by testing model on AIA or EUVI data
   `./Scripts/test_UV_GAN.sh` or   
   `sbatch ./Scripts/test_UV_GAN.sh` (Monarch). See `test_UV_GAN.sh` for
   additional settings such as # itterations, model name etc.

## Plotting:
- Plot percentiles of the different data types: 
   `python Plotting/plot_percentiles.py`  
- View a numpy array from file (enter in path to file when prompted): 
   `python Plotting/view_specific_npy.py`  
