# Sun_GAN

## Environments
### Data processing
The file `conda_spec-list.txt` specifies the conda environment used for all data processing tasks.
A similar conda environment can be made using the command:
`conda create --prefix ./data_env`
`conda activate ./data_env/`
`conda install --file conda_spec-list.txt`

### Training/Testing
Training and testing of each GAN was done in a [Monarch](https://docs.monarch.erc.monash.edu/) environment created using the following commands:

`module load anaconda/5.1.0-Python3.6-gcc5`
`module load cudnn/7.6.5-cuda10.1`
`module load tensorflow/2.3.0`


