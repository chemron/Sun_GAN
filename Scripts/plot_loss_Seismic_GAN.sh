model=Seismic_GAN_1

python Plotting/plot_loss.py <(awk '{print $4, $9, $11, $13}' Models/$model/iter_loss.txt)