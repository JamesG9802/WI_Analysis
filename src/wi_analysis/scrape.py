"""Webscrapes the Wandering inn website and downloads the files to a specified location.
"""

import json
import logging
import os
from os import path
import random
import time
from typing import Final, List, TypedDict

from bs4 import BeautifulSoup
import requests

from scrape_get_args import get_args

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


DEFAULT_CONFIG_PATH: Final[os.PathLike] = "config.json"
"""The default path to the config.json.
"""

DEFAULT_DATABASE_PATH: Final[os.PathLike] = "raw_database"
"""The default path to the database folder.
"""

TABLE_OF_CONTENTS_FILE_NAME: Final[os.PathLike] = "table_of_contents.html"
"""The name of the table of contents file.
"""


USER_AGENTS: List[str] = [
    # Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    # Safari (Mac)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
]


class ConfigJSON(TypedDict):
    table_of_contents: str
    """The URL to the table of contents.
    """

def download(url: str, file_path: os.PathLike) -> bool:
    """Downloads a URL and saves it to a file

    Args:
        url (str): the URL to fetch the document.
        file_path (os.PathLike): the file path to save to.

    Raises:
        Exception: If there is an error getting the URL or saving the file.

    Returns:
        bool: whether the download succeeded.
    """
    try:
        request = requests.get(url, headers=
            {
                "Content-Type": "text/html; charset=utf-8",
                "User-Agent": USER_AGENTS[random.randrange(0, len(USER_AGENTS))]
            }
        )
        
        if request.status_code != 200:
            raise Exception(f"Status code: {request.status_code}")
        
        contents = request.text
        
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(contents)

        return True
    except Exception as e:
        logger.exception(e)
        logger.warning(f"Failed to download {url}.")
        logger.debug(contents)
        return False

def get_chapter_urls(table_of_contents_filepath: str) -> List[str]:
    """Returns all the chapter URLs from the table of contents/

    Args:
        table_of_contents_filepath (str): the local file path to the table of contents HTML.

    Returns:
        List[str]: a list of each URL in sequential order.
    """
    with open(table_of_contents_filepath, "r") as file:
        contents = file.read()
        soup = BeautifulSoup(contents, "html.parser")

        entries = soup.find_all(class_="chapter-entry") 

        return [entry.contents[0].contents[0]["href"] for entry in entries]

def main():
    args = get_args()

    config_filepath: os.PathLike = args.config
    database_filepath: os.PathLike = args.database
    scrape_delay: float = args.timedelay
    should_refetch: bool = args.refetch
    start_index: int = args.start
    end_index: int = args.end

    config: ConfigJSON = None

    if config_filepath == None or not path.isfile(config_filepath):
        logger.warning(f"Config path '{config_filepath}' not found. Falling back to '{DEFAULT_CONFIG_PATH}'.")
        if not path.isfile(DEFAULT_CONFIG_PATH):
            logger.error(f"Couldn't open default config path '{DEFAULT_CONFIG_PATH}'.")
            return -1
        else:
            config_filepath = DEFAULT_CONFIG_PATH

    with open(config_filepath, "r") as file:
        config = json.load(file)
    
    if database_filepath == None or not path.isdir(database_filepath):
        logger.warning(f"Database path '{database_filepath}' not found. Falling back to '{DEFAULT_DATABASE_PATH}'.")
        if not path.isdir(DEFAULT_DATABASE_PATH):
            #   Try to make the directory if possible
            os.mkdir(DEFAULT_DATABASE_PATH)
            if not path.isdir(DEFAULT_DATABASE_PATH):
                logger.error(f"Couldn't open or create default database path '{DEFAULT_DATABASE_PATH}'.")
                return -1
        else:
            database_filepath = DEFAULT_DATABASE_PATH

    if should_refetch or not path.isfile(TABLE_OF_CONTENTS_FILE_NAME):
        download(config["table_of_contents"], TABLE_OF_CONTENTS_FILE_NAME)

    urls = get_chapter_urls(TABLE_OF_CONTENTS_FILE_NAME)

    if start_index == None:
        start_index = 0
    if end_index == None:
        end_index = len(urls)

    for i in range(start_index, end_index):
        logger.info(f"Downloading i: {i} - {urls[i]}.")
        success = download(urls[i], path.join(database_filepath, f"{i}_"+path.basename(urls[i].strip("/"))))
        
        if not success:
            return -1
        
        time.sleep(scrape_delay)

    return 0

if __name__ == "__main__":
    exit(main())