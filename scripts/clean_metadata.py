"""Script for cleaning the character template metadata"""

import json
import logging
from pathlib import Path
from tqdm.auto import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_PATH = Path(__file__).parent.parent / "data"
TEMPLATE_DATA_PATH = DATA_PATH / "character_templates"


def flatten_value(value):
    if isinstance(value, list):
        if not value:
            return ""
        return value[0] if len(value) == 1 else ", ".join(map(str, value))
    elif isinstance(value, dict):
        value_str = ", ".join(f"{k}: {v[0]}" for k, v in value.items())
        return value_str


def main():
    with open(
        TEMPLATE_DATA_PATH / "dnd_chars_unique.json",
        "r",
        encoding="utf-8",
    ) as file:
        uncleaned_template_data = json.load(file)
    cleaned_template_data = {}
    for char_summary, unclean_char_template in tqdm(uncleaned_template_data.items()):
        class_key = next(iter(unclean_char_template["class"]))
        clean_char_template = {
            "hash": unclean_char_template["hash"][0],
            "race": unclean_char_template["race"]["race"][0],
            "background": unclean_char_template["background"][0],
            "class": unclean_char_template["class"][class_key]["class"][0],
            "subclass": unclean_char_template["class"][class_key]["subclass"][0],
            "level": unclean_char_template["level"][0],
            "feats": flatten_value(unclean_char_template["feats"]),
            "HP": unclean_char_template["HP"][0],
            "AC": unclean_char_template["AC"][0],
            "attributes": flatten_value(unclean_char_template["attributes"]),
            "alignment": unclean_char_template["alignment"]["alignment"][0],
            "skills": flatten_value(unclean_char_template["skills"]),
            "weapon": next(iter(unclean_char_template["weapons"]), ""),
        }
        cleaned_template_data[char_summary] = clean_char_template
    with open(
        TEMPLATE_DATA_PATH / "dnd_templates_cleaned.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(cleaned_template_data, file, indent=2)
    logger.info("Character templates cleaned!")


if __name__ == "__main__":
    main()
