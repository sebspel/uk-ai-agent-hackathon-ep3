"""Load and process dialogue data"""

import json
import logging
from pathlib import Path

import chromadb
from tqdm.auto import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_PATH = Path(__file__).parent.parent / "data"
DIALOGUE_DATA_PATH = DATA_PATH / "dialogue_data"
TEMPLATE_DATA_PATH = DATA_PATH / "character_templates"


def main():
    db = chromadb.PersistentClient(
        path="./chromadb",
    )

    # Create and populate dialogue collection
    dialogue_collection = db.create_collection(
        name="character_dialogue",
        metadata={"hnsw:space": "cosine"},
    )
    counter = 0
    for json_file in tqdm(DIALOGUE_DATA_PATH.rglob("*.json")):
        with open(json_file, "r", encoding="utf-8") as file:
            dialogue_data = json.load(file)
        for chunk in dialogue_data:
            for turn in chunk["TURNS"]:
                # Skip if Matt Mercer is the only speaker
                if turn["NAMES"] == "MATT":
                    continue
                dialogue_collection.add(
                    documents=" ".join(turn["UTTERANCES"]),
                    ids=[f"{counter}"],
                )
                counter += 1
    logger.info("JSON dialogue extraction complete")

    # Create and populate template collection
    template_collection = db.create_collection(
        name="character_templates",
        metadata={"hnsw:space": "cosine"},
    )
    with open(
        TEMPLATE_DATA_PATH / "dnd_chars_unique.json",
        "r",
        encoding="utf-8",
    ) as file:
        template_data = json.load(file)

    for char_summary, char_template in template_data.items():
        template_collection.add(
            documents=[char_summary],
            metadatas=[char_template],
            ids=[char_template["finger"]],
        )

    logger.info("JSON unique character template extraction complete")


if __name__ == "__main__":
    main()
