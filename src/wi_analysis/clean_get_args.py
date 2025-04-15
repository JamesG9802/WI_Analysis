from argparse import ArgumentParser, Namespace

def get_args() -> Namespace:
    """Returns the command line arguments for clean.

    Returns:
        Namespace: the arguments.
    """
    parser: ArgumentParser = ArgumentParser()

    parser.add_argument(
        "source",
        type=str,
        help="The source directory to read from."
    )

    parser.add_argument(
        "target",
        type=str,
        help="The target directory to store files in."
    )

    parser.add_argument(
        "--overwrite",
        "-o",
        action="store_true",
        help="Whether to overwrite the contents in the target directory."
    )

    return parser.parse_args()

