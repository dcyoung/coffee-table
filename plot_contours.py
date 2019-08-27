import os
import os.path as osp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tqdm import tqdm
import PIL


def plot_contours(ax, data, levels=5, cmap="binary"):
    # z = -(data - np.amax(data))
    z = data
    x, y = np.meshgrid(range(z.shape[0]), range(z.shape[1]))

    # plot
    ax.contourf3D(x, y, np.transpose(z), 50, cmap=cmap, levels=levels)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title("Depth as 3d contours. levels={0}".format(levels))
    ax.set_xlabel("X (100 m)")
    ax.set_ylabel("Y (100 m)")
    ax.set_zlabel("Z (m)")
    ax.view_init(30, 45)


def main(args):
    print("Reading file...")
    depth_grid = np.loadtxt(args.input, skiprows=7)
    depth_grid = np.clip(depth_grid, a_min=0, a_max=None)

    im = depth_grid - depth_grid.min()
    im *= 255.0 / im.max()
    im = im.astype(np.uint8)
    im = PIL.Image.fromarray(im)

    os.makedirs(args.output, exist_ok=True)

    print("Creating plots...")
    for n_clusters in tqdm(range(4, 64, 4)):
        quant = im.quantize(n_clusters)
        arr = np.array(quant)

        fig = plt.figure()

        # Plot quantized heatmap
        ax = fig.add_subplot(121)
        p = plt.imshow(quant)
        plt.colorbar(p)
        ax.set_title("Quantized: {0} clusters".format(n_clusters))

        # Plot contours
        ax = fig.add_subplot(122, projection="3d")
        plot_contours(ax=ax, data=arr, levels=args.levels, cmap="viridis")
        # invert
        # plot_contours(
        #     ax=ax, data=-(arr - np.amax(arr)), levels=args.levels, cmap="viridis"
        # )

        if args.viz:
            plt.show()

        plt.savefig(
            osp.join(
                args.output,
                "quantized_{0}_levels_{1}.png".format(n_clusters, args.levels),
            ),
            dpi=500
        )

        plt.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        default=osp.join("resources", "bathymetry", "FullBay100", "msl1k.asc"),
        help="Path to GIS ASCII data file.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=osp.join("output", "contour_templates"),
        help="Path to write plots.",
    )
    parser.add_argument(
        "--levels",
        type=int,
        default=5,
        help="The number of evenly spaced contour levels.",
    )
    parser.add_argument(
        "--viz", action="store_true", help="If included, show results on screen."
    )
    args = parser.parse_args()

    print(args)
    main(args)
