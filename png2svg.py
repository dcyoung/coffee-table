import subprocess
from tempfile import NamedTemporaryFile

from PIL import Image


def main(args):
    with Image.open(args.input) as im:
        with NamedTemporaryFile("w", suffix=".pnm") as f:
            im.save(f.name)
            subprocess.run(["potrace", f.name, "-s", "-o", args.output])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default=None, help="path to an image file")
    parser.add_argument(
        "--output", type=str, default=None, help="Path to write output svg.",
    )
    args = parser.parse_args()

    print(args)
    main(args)
