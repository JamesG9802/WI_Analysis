from argparse import ArgumentParser, Namespace

def get_args() -> Namespace:
    """Returns the command line arguments for analyze.

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
        help="The target file to write the analysis to."
    )

    parser.add_argument(
        "--append",
        action="store_true",
        help="Whether to append stats to the target file."
    )

    parser.add_argument(
        "--color",
        action="store_true",
        help="Whether to analyze the color of tags. The source directory must be an XML document."
    )

    parser.add_argument(
        "--levels",
        action="store_true",
        help="Whether to analyze the levels, skills, and classes."
    )


    return parser.parse_args()

