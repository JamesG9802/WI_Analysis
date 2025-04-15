"""Cleans up the raw HTML content for better processing.
"""

import logging
import os
from os import path

from bs4 import BeautifulSoup

from clean_get_args import get_args

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S %p')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

def clean_files(source_dir: os.PathLike, target_dir: os.PathLike):
    """Cleans up every file in the source directory and saves it in the target directory.

    Args:
        source_dir (os.PathLike): the source directory.
        target_dir (os.PathLike): the target directory.
    """

    for file_name in os.listdir(source_dir):
        logger.info(file_name)
        with open(path.join(source_dir, file_name), "r", encoding="utf-8") as read_file:
            raw_content = read_file.read()
            soup = BeautifulSoup(raw_content, "html.parser")

            main_content = soup.find(class_="entry-content").text
            with open(path.join(target_dir, file_name), "w", encoding="utf-8") as write_file:
                write_file.write(main_content)

def main():
    args = get_args()

    source_dir: os.PathLike = args.source
    target_dir: os.PathLike = args.target
    should_overwrite: bool = args.overwrite

    if not path.isdir(source_dir):
        logger.error(f"Source directory ({source_dir}) is not a valid directory.")
        return -1
    if not path.isdir(target_dir):
        logger.error(f"Target directory ({target_dir}) is not a valid directory.")
        return -1
    
    if not should_overwrite:
        with os.scandir(target_dir) as iterator:
            if any(iterator):
                logger.error(f"Target directory ({target_dir}) is not empty. Consider setting --overwrite or -o.")
                return -1
    
    clean_files(source_dir, target_dir)
    return 0

if __name__ == "__main__":
    exit(main())