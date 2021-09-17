# Sun_GAN
See 
[my honours thesis](https://github.com/chemron/honours_thesis/blob/master/thesis.pdf)
for a full description of the system. 

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

These can similarly be unloaded by using the commands:
`module unload anaconda/5.1.0-Python3.6-gcc5`  
`module unload cudnn/7.6.5-cuda10.1`  
`module unload tensorflow/2.3.0`  

## Pipeline: Data Preparation
The pipeline for downloading and preparing the data used throughout this project.
### Data collection
Download fits data (SDO AIA/HMI, STEREO EUVI and phase maps):  
  `./Scripts/Data_collection.sh` or  
  `sbatch ./Scripts/Data_collection.sh` (Monarch).  
The STEREO data is downloaded such that it is synchronised with the phase maps.

### Data processing
The processing pipleine consists of
1. Converting SDO and STEREO fits data into local numpy arrays (.npy), and get
   percentiles of the data
2. Reproject the seismic maps (phase maps) from a Carrington Heliographic
   projection to a Helioprojective-cartesian projection, convert to numpy arrays
   and get percentiles.
3. Remove outliers in each dataset
4. change saturation for EUV and magnetogram data
5. normalise data (put data between -1 and 1 for magnetograms, and between 0 and
   1 for the other datasets)
6. Remove trends in EUV data caused by instrument degredation
7. Create a database (`image.db`) that maps the connections between the different
   data types  

The data processing pipeline can be run as follows:
`./Scripts/data_processing.sh` or   
`sbatch ./Scripts/data_processing.sh` (Monarch).  

## Pipeline: UV-GAN
The pipeline for generating synthetic magnetograms from EUV 304 Angstrom
full-disk solar images. Trains by comparing SDO EUV images with SDO
magnetograms. It is a good idea to initially run the GAN for a small number of
itterations (e.g. 20) to ensure everything is working as it should before
running a full scale model.  
1. Train model on SDO AIA EUV images and SDO HMI magnetograms:  
   `./Scripts/train_UV_GAN.sh` or   
   `sbatch ./Scripts/train_UV_GAN.sh` (Monarch). See `train_UV_GAN.sh` for
   additional settings such as # itterations, model name etc.
2. Evaluate model by testing model on AIA and EUVI data
   `./Scripts/test_UV_GAN.sh` or   
   `sbatch ./Scripts/test_UV_GAN.sh` (Monarch). See `test_UV_GAN.sh` for
   additional settings such as # itterations, model name etc. This additionally
   applies a mask to selected outputs to aid in training the seismic GAN

## Pipeline: Seismic-GAN
The pipeline for generating synthetic magnetograms from farside seismic maps.
Trains by comparing farside seismic maps to synthetic magnetograms generated
from STEREO EUV data. It is a good idea to initially run the GAN for a small
number of itterations (e.g. 20) to ensure everything is working as it should
before running a full scale model.  
1. Train model on seismic maps and synthetic STEREO magnetograms:  
   `./Scripts/train_seismic_GAN.sh` or   
   `sbatch ./Scripts/train_seismic_GAN.sh` (Monarch). See `train_seismic_GAN.sh` for
   additional settings such as # itterations, model name etc.
2. Evaluate model by testing model on seismic maps
   `./Scripts/test_seismic_GAN.sh` or   
   `sbatch ./Scripts/test_seismic_GAN.sh` (Monarch). See `test_seismic_GAN.sh` for
   additional settings such as # itterations, model name, testing set etc.

## Plotting:
- Plot percentiles of the different data types: 
   `python Plotting/plot_percentiles.py`  
- View a numpy array from file (enter in path to file when prompted): 
   `python Plotting/view_specific_npy.py`  
