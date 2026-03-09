"""Download CROHME 2023 dataset from Zenodo.

Usage:
    python data/datasets/scripts/download_crohme.py

Downloads InkML files to data/datasets/crohme/raw/
"""

import os
import subprocess
import zipfile
from pathlib import Path

DATASET_DIR = Path(__file__).resolve().parents[1] / "crohme"
RAW_DIR = DATASET_DIR / "raw"

# Direct download URL with ?download=1 for Zenodo
DOWNLOAD_URL = "https://zenodo.org/records/8428035/files/CROHME23.zip?download=1"
LOCAL_FILENAME = "CROHME23.zip"


def download_file(url, dest):
    """Download a file using curl or wget."""
    if dest.exists() and dest.stat().st_size > 1_000_000:
        print("  Already downloaded: %s (%d MB)" % (dest.name, dest.stat().st_size // 1_000_000))
        return

    # Remove any partial/bad downloads
    if dest.exists():
        dest.unlink()

    print("  Downloading %s..." % dest.name)
    try:
        subprocess.run(
            ["curl", "-L", "-o", str(dest), url],
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(
            ["wget", "-O", str(dest), url],
            check=True,
        )


def extract_archive(archive_path):
    """Extract a zip file. Uses system unzip for large/ZIP64 files."""
    print("  Extracting %s..." % archive_path.name)
    try:
        # Try system unzip first (handles ZIP64 better than Python 3.9)
        subprocess.run(
            ["unzip", "-o", "-q", str(archive_path), "-d", str(RAW_DIR)],
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to Python zipfile
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(RAW_DIR)
    print("  Extracted to %s" % RAW_DIR)


def count_inkml_files():
    """Count .inkml files in the raw directory."""
    count = 0
    for f in RAW_DIR.rglob("*.inkml"):
        count += 1
    return count


def main():
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    archive_path = DATASET_DIR / LOCAL_FILENAME

    print("Downloading CROHME 2023 dataset from Zenodo...")
    download_file(DOWNLOAD_URL, archive_path)

    print("\nExtracting archive...")
    extract_archive(archive_path)

    inkml_count = count_inkml_files()
    print("\nFound %d InkML files in %s" % (inkml_count, RAW_DIR))

    if inkml_count == 0:
        print("\nNo InkML files found. The archive structure may differ.")
        print("Please check %s and adjust if needed." % RAW_DIR)
        print("Manual download: https://zenodo.org/records/8428035")
    else:
        print("\nDownload complete! Next step: run convert_crohme.py to render images.")


if __name__ == "__main__":
    main()
