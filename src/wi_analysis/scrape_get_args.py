from argparse import ArgumentParser, Namespace

def get_args() -> Namespace:
    """Returns the command line arguments for scrape.

    Returns:
        Namespace: the arguments.
    """
    parser: ArgumentParser = ArgumentParser()

    parser.add_argument(
        "--config",
        "-c",
        type=str,
        help="The config file to read from."
    )

    parser.add_argument(
        "--database",
        "-d",
        type=str,
        help="The database folder where files are stored."
    )

    parser.add_argument(
        "--timedelay",
        "-t",
        type=float,
        help="The delay between scraping new web pages in seconds. Note that scraping too fast will result in being flagged by WordPress.",
        default=120
    )

    parser.add_argument(
        "--refetch",
        "-r",
        action="store_true",
        help="Whether to refetch the the table of contents."
    )

    parser.add_argument(
        "--start",
        "-s",
        type=int,
        help="The starting index of chapters to download. Inclusive."
    )

    parser.add_argument(
        "--end",
        "-end",
        type=int,
        help="The end index of chapters to download. Exclusive."
    )

    return parser.parse_args()

