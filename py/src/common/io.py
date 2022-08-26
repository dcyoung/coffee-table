from pathlib import Path
from typing import List

BATHY_FILE_EXTS = {".asc", ".geo.tif", ".geotif", ".tif"}


def list_bathy_files(parent_dir: Path) -> List[Path]:
    assert parent_dir.is_dir()

    targets = []
    for ext in BATHY_FILE_EXTS:
        targets += parent_dir.rglob(f"*{ext.lower()}") + parent_dir.rglob(
            f"*{ext.upper()}"
        )
    return list(set(targets))
