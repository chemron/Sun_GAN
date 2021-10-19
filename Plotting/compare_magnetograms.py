import matplotlib.pyplot as plt
import os
import sys
import argparse
import gc
import matplotlib
sys.path.insert(1, './Data_processing')
import plot_specific_magnetogram as mag_plot
from sql_util import create_connection, execute_read_query

connection = create_connection("./image.db")
matplotlib.use('Agg')


parser = argparse.ArgumentParser()
parser.add_argument("--UV_GAN_iter", type=int, default=500000)
parser.add_argument("--UV_GAN_model", default="UV_GAN_1")
parser.add_argument("--Seismic_GAN_iter", type=int, default=500000)
parser.add_argument("--Seismic_GAN_model", default="Seismic_GAN_1")
args = parser.parse_args()


def plot_comparison(synthetic_mag, true_mag, v):
    if (synthetic_mag in (None, "NULL")) or (true_mag in (None, "NULL")):
        return
    else:
        path_tree = synthetic_mag.split("/")
        png_dir = "/".join(path_tree[:-1]) + "_comparison/"
        name = path_tree[-1].strip(".npy")
        os.makedirs(png_dir) if not os.path.exists(png_dir) else None

        # setup figure
        fig = plt.figure(1, figsize=(10, 5))

        # plot synthetic mag

        plt.subplot(1, 2, 1)
        plt.title(r"Predicted line-of-sight Magnetic field")
        mag_plot.plot_magnetogram(synthetic_mag, v, colorbar=False)

        # plot true mag
        plt.subplot(1, 2, 2)
        plt.title(r"True line-of-sight Magnetic field")
        mag_plot.plot_magnetogram(true_mag, v, colorbar=False)

        # plot colorbar
        cbar = plt.colorbar(ax=fig.axes, shrink=0.8)
        cbar.set_label(r"Magnetic Field Strength [$G$]")
        print(name)
        plt.tight_layout
        plt.savefig(
            f"{png_dir}/{name}.png", dpi=300,
            facecolor="w", bbox_inches='tight'
            )
        plt.cla()
        plt.clf()
        plt.close('all')
        plt.close(fig)
        del fig, cbar
        gc.collect()


if __name__ == "__main__":
    UV_GAN_str = f"{args.UV_GAN_model}_iter_{args.UV_GAN_iter:0>7}_path"
    print("UV GAN string: ", UV_GAN_str)
    Seismic_GAN_str = \
        f"{args.Seismic_GAN_model}_iter_{args.Seismic_GAN_iter:0>7}_path"
    print("Seismic GAN string: ", Seismic_GAN_str)

    select_UV_GAN = f"""
    SELECT
        aia.{UV_GAN_str},
        hmi.np_path_normal
    FROM
        aia,
        hmi
    WHERE
        aia.hmi_id=hmi.id
    GROUP BY
        hmi.id
    """

    select_Seismic_GAN = f"""
    SELECT
        phase_map.{Seismic_GAN_str},
        euvi.{UV_GAN_str}
    FROM
        phase_map,
        euvi
    WHERE
        phase_map.euvi_id=euvi.id
    GROUP BY
        euvi.id
    """
    UV_GAN_magnetograms = execute_read_query(connection,
                                             select_UV_GAN)
    Seismic_GAN_magnetograms = execute_read_query(connection,
                                                  select_Seismic_GAN)

    v = 4000
    for synthetic_mag, true_mag in UV_GAN_magnetograms:
        plot_comparison(synthetic_mag, true_mag, v)

    for synthetic_mag, true_mag in Seismic_GAN_magnetograms:
        plot_comparison(synthetic_mag, true_mag, v)
