# Disclaimer

Disclaimer: This is an independent software pacakage created to parse and handle content from *The Wandering Inn*. It is not affiliated with or endorsed by *The Wandering Inn*. 

This package is designed to scrape data from *The Wandering Inn* website, as of 4/8/2025. Any changes to the website since then may break this code. The chapter contents are copyrighted and not publically available from this repository.

Stats are available in `Stats/`.

# Usage

This project uses Poetry for dependency management. 
[See Poetry's page for getting started.](https://python-poetry.org/docs/#installing-with-pipx)

Alternatively, you can install directly from the `requirements.txt` file.

[See Python's page for getting started.](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#using-a-requirements-file)

To run this project, run `scrape.py` like:

`poetry run python src/wi_analysis/scrape.py`

or

`python src/wi_analysis/scrape.py`

If no command line arguments are passed, then it will attempt to read the `config.json` file and write to the `raw_database/` folder.
It will fetch the `table_of_contents.html` page and store it locally. If it already exists, it will simply use the local version unless a new one is requested with:

`python src/wi_analysis/scrape.py --refetch`

It will then attempt to download chapters one-by-one based on the table of contents. A default time delay of 60 seconds is used between fetching pages.

Once all the chapters are downloaded, you can optionally run `clean.py` to strip out excess HTML data and produce the raw text. For example:

`python src/wi_analysis/analyze.py raw_database clean_database`

will read the chapters from the `raw_database/` folder and output them to `clean_database/`.

You can then analyze the chapters with `analyze.py`. It currently supports the following options:
- `--colors` to find color data (only works on the raw HTML files).
- `--levels` to find all bracketed instances of levels, classes, and skills mentioned in the story.


For example:
`python src/w_analysis/analyze raw_database stats.json --colors`

This will write color stats to the `stats.json` file.