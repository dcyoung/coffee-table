import os
import os.path as osp
from pathlib import Path
from typing import List
import zipfile

BATHY_FILE_EXTS = {".asc", ".geo.tif", ".geotif", ".tif"}


def list_bathy_files(parent_dir: Path) -> List[Path]:
    assert parent_dir.is_dir()

    targets = []
    for ext in BATHY_FILE_EXTS:
        targets += parent_dir.rglob(f"*{ext.lower()}") + parent_dir.rglob(
            f"*{ext.upper()}"
        )
    return list(set(targets))


def make_zip_archive(src_path, dst_path):
    with zipfile.ZipFile(dst_path, "w") as archive:
        for (dirpath, _, filenames) in os.walk(src_path):
            for name in filenames:
                path = osp.join(dirpath, name)
                archive.write(path, osp.relpath(path, src_path))
