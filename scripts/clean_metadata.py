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
    """Convert complex nested data structures into flat string representations.

    Handles lists and dictionaries by flattening them into comma-separated strings.
    This is useful for converting nested character template data into searchable text.

    Args:
        value: The value to flatten. Can be a list, dict, or any other type.

    Returns:
        - Empty string if value is an empty list
        - First element if value is a single-item list
        - Comma-separated string if value is a multi-item list
        - Formatted string "key: value" for dictionaries
        - None for non-list, non-dict values

    Examples:
        >>> flatten_value(["Strength"])
        "Strength"
        >>> flatten_value(["Sword", "Shield", "Armor"])
        "Sword, Shield, Armor"
        >>> flatten_value({"Strength": [15], "Dexterity": [12]})
        "Strength: 15, Dexterity: 12"
    """
    if isinstance(value, list):
        if not value:
            return ""
        return value[0] if len(value) == 1 else ", ".join(map(str, value))
    elif isinstance(value, dict):
        value_str = ", ".join(f"{k}: {v[0]}" for k, v in value.items())
        return value_str


def main():
    """Clean and flatten the character template metadata from the raw JSON format.

    Reads the raw unique character data with nested structures and converts it into
    a simplified, flat format suitable for ChromaDB storage and retrieval.

    The cleaning process:
    1. Loads raw character templates from dnd_chars_unique.json
    2. Extracts and flattens nested character attributes (race, class, level, etc.)
    3. Converts complex nested dictionaries into simple key-value pairs
    4. Saves the cleaned data to dnd_templates_cleaned.json

    Character attributes cleaned:
        - hash: Unique identifier
        - race, background, class, subclass, level: Character basics
        - feats, skills, attributes: Flattened from lists/dicts
        - HP, AC: Combat stats
        - alignment: Character alignment
        - weapon: Primary weapon (first from weapons list)

    Input file: data/character_templates/dnd_chars_unique.json
    Output file: data/character_templates/dnd_templates_cleaned.json
    """
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
