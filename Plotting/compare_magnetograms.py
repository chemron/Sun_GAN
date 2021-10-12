import matplotlib.pyplot as plt
import os
import plot_specific_magnetogram as mag_plot
import sys
sys.path.insert(1, './Data_processing')
from sql_util import create_connection, execute_read_query
connection = create_connection("./image.db")
plt.switch_backend("agg")


def plot_comparison(synthetic_mag, true_mag, v):
    if (synthetic_mag in (None, "NULL")) or (true_mag in (None, "NULL")):
        return
    else:
        path_tree = synthetic_mag.split("/")
        png_dir = "/".join(path_tree[:-1]) + "_comparison/"
        name = path_tree[-1].strip(".npy")
        os.makedirs(png_dir) if not os.path.exists(png_dir) else None

        # setup figure
        plt.figure(1, figsize=(15, 5))

        # plot synthetic mag
        
        plt.subplot(1, 2, 1)
        plt.title(r"Predicted line-of-sight Magnetic field [$G$]")
        mag_plot.plot_magnetogram(synthetic_mag, v)

        # plot true mag
        plt.subplot(1, 2, 2)
        plt.title(r"True line-of-sight Magnetic field [$G$]")
        mag_plot.plot_magnetogram(true_mag, v)

        print(name)
        plt.savefig(f"{png_dir}/{name}.png", dpi=300)
        plt.close(1)


select_UV_GAN = """
SELECT
    aia.UV_GAN_1_iter_0500000_path,
    hmi.np_path_normal
FROM
    aia,
    hmi
WHERE
    aia.hmi_id=hmi.id
GROUP BY
    hmi.id
"""

select_Seismic_GAN = """
SELECT
    phase_map.Seismic_GAN_1_iter_0500000_path,
    euvi.UV_GAN_1_iter_0500000_path
FROM
    phase_map,
    euvi
WHERE
    phase_map.euvi_id=euvi.id
GROUP BY
    euvi.id
"""

UV_GAN_magnetograms = execute_read_query(connection, select_UV_GAN)
Seismic_GAN_magnetograms = execute_read_query(connection, select_Seismic_GAN)


v = 4000
for synthetic_mag, true_mag in UV_GAN_magnetograms:
    plot_comparison(synthetic_mag, true_mag, v)

for synthetic_mag, true_mag in Seismic_GAN_magnetograms:
    plot_comparison(synthetic_mag, true_mag, v)
