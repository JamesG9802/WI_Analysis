"""Analyzes a database of Wandering Inn HTML files (cleaned or raw).
"""

import json
import logging
import os
from os import path
import re
from typing import Any, Dict

from bs4 import BeautifulSoup

from analyze_get_args import get_args

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

class CaseInsensitiveStr(str):
    def __eq__(self, other):
        if isinstance(other, str):
            return self.casefold() == other.casefold()
        return NotImplemented

    def __hash__(self):
        return hash(self.casefold())

def analyze_color(source_dir: os.PathLike) -> Dict[str, int]:
    """Analyzes the color of tags from a source directory.

    Args:
        source_directory (os.PathLike): a source directory of XML documents.
    
    Returns:
        Dict[str, int]: a dictionary of colors to their frequency.
    """

    colors: Dict[str, int] = dict()

    for file_name in os.listdir(source_dir):
        with open(path.join(source_dir, file_name), "r", encoding="utf-8") as read_file:
            raw_content = read_file.read()
            soup = BeautifulSoup(raw_content, "html.parser")

            main_content = soup.find(class_="entry-content")

            spans = main_content.find_all("span", style=True)

            for span in spans:
                #   Extract the color, if it exists
                match = re.search(r'color\s*:\s*(#[0-9a-fA-F]{3,6})', span["style"])
                if not match:
                    continue
                color = match.group(1)
                if color not in colors:
                    logger.info(f"color {file_name} {color}")
                    colors[color] = 1
                else:
                    colors[color] += 1
    return colors

def analyze_levels(source_dir: os.PathLike) -> Dict[str, Dict]:
    """Analyzes the skills, levels, and classes.

    Args:
        source_directory (os.PathLike): a source directory of files.
    
    Returns:
        Dict[str, int]: a dictionary of colors to their frequency.
    """
    levels: Dict[CaseInsensitiveStr, int] = dict()
    classes: Dict[CaseInsensitiveStr, int] = dict()
    skills: Dict[CaseInsensitiveStr, int] = dict()
    unknown: Dict[CaseInsensitiveStr, int] = dict()

    
    def insert_dict(dict: Dict, obj: str, name: str | None = None):
        """Insert a string into a dictionary.

        Args:
            dict (Dict): the dictionary.
            obj (str): the string object.
            name (str | None, optional): Name of the dictionary for logging. Defaults to None.
        """
        if obj not in dict:
            name = name if name != None else ""
            logger.debug(f"{name} {file_name} {obj}")
        string = CaseInsensitiveStr(obj)
        dict[string] = dict.setdefault(string, 0) + 1

    for file_name in os.listdir(source_dir):
        with open(path.join(source_dir, file_name), "r", encoding="utf-8") as read_file:
            content = read_file.read()

            bracket_matches = re.findall(r"\[(?=[^—…])(.*?[^—])(?=[^—…])\]", content)

            for bracket_match in bracket_matches:
                skill_match = re.search(r"^(?:Temporary\s)?Skill\s[–—]\s(.*?)\s(?:[oO]btained|[lL]earned|[aA]ssigned)[.!]?$", bracket_match)
                skill_assigned_match = re.search(r"^(?:Temporary\s)?Skill\s[–—]\s(.*?)\s[aA]ssigned[.!]?$", bracket_match)
                skillchange_match = re.search(r"^Skill\sChange\s[–—]\s(.*?)\s→\s(.*?)[.!]?$", bracket_match)
                levelup_match = re.search(r"^(.*?)\sLevel\s[0-9]+[.!]?$", bracket_match)
                classobtained_match = re.search(r"^(.*?)\s[cC]lass\s[oO]btained[.!]?$", bracket_match)
                classdown_match = re.search(r"^(.*?)\sLevel\s[0-9]+\s→\s(.*?)\sLevel\s[0-9]+[.!]?$", bracket_match)
                conditionsmet1_match = re.search(r"^Class\sConsolidation:\s(.*?)\s[rR]emoved[.!]?$", bracket_match)
                conditionsmet2_match = re.search(r"^Class\sConsolidation:\s(.*?)\s→\s(.*?)\s[.!]?$", bracket_match)
                conditionsmet3_match = re.search(r"^Conditions Met:\s(.*?)\s→\s(.*?)(?:\s[cC]lass)?[.!]?$", bracket_match)

                if skill_match:
                    insert_dict(skills, skill_match.group(1), "skills")
                elif skill_assigned_match:
                    insert_dict(skills, skill_assigned_match.group(1), "skills")
                elif skillchange_match:
                    insert_dict(skills, skillchange_match.group(2), "skills")
                    insert_dict(skills, skillchange_match.group(2), "skills")
                elif levelup_match: #   levels are not gathered; they are done through a more exhaustive search
                    insert_dict(classes, levelup_match.group(1), "classes")
                elif classobtained_match:
                    insert_dict(classes, classobtained_match.group(1), "classes")
                elif classdown_match:
                    insert_dict(classes, classdown_match.group(1), "classes")
                    insert_dict(classes, classdown_match.group(2), "classes")
                elif conditionsmet1_match:
                    insert_dict(classes, conditionsmet1_match.group(1), "classes")
                elif conditionsmet2_match:
                    insert_dict(classes, conditionsmet2_match.group(1), "classes")
                    insert_dict(classes, conditionsmet2_match.group(2), "classes")
                elif conditionsmet3_match:
                    insert_dict(classes, conditionsmet3_match.group(1), "classes")
                    insert_dict(classes, conditionsmet3_match.group(2), "classes")
                else:
                    insert_dict(unknown, bracket_match, "unknown")

            level_matches = re.findall(r"Level ([0-9]+)", content)
            for level_match in level_matches:
                if level_match not in levels:
                    logger.debug(f"level {file_name} {level_match}")
                levels[level_match] = levels.setdefault(level_match, 0) + 1

    #   Do a pass on the unknown to remove obvious matches
    for key, value in unknown.items():
        if key in classes:
            classes[key] += value
            unknown[key] = 0
        elif key in skills:
            skills[key] += value
            unknown[key] = 0

    return_dict: Dict[str, Dict] = dict()
    return_dict["levels"] = levels
    return_dict["classes"] = classes
    return_dict["skills"] = skills
    return_dict["unknown"] = { key: value for key, value in unknown.items() if value != 0 } 

    return return_dict

def main():
    args = get_args()
    source_dir: os.PathLike = args.source
    target_file: os.PathLike = args.target

    should_append: bool = args.append
    should_analyze_color: bool = args.color
    should_analyze_levels: bool = args.levels

    stats: Dict[str, Any] = dict()

    if not path.isdir(source_dir):
        logger.error(f"Source directory ({source_dir}) is not a valid directory.")
        return -1

    if should_append and path.isfile(target_file):
        with open(target_file, "r") as file:
            stats = json.load(file)

    if should_analyze_color:
        stats["color"] = analyze_color(source_dir)

    if should_analyze_levels:
        stats["levelling"] = analyze_levels(source_dir)

    with open(target_file, "w", encoding="utf-8") as write_file:
        write_file.write(json.dumps(stats))

    return 0

if __name__ == "__main__":
    exit(main())