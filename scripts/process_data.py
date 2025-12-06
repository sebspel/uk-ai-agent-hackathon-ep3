"""Load and process dialogue data"""

import json
import logging
from pathlib import Path

import torch
import chromadb
from chromadb.errors import NotFoundError
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from tqdm.auto import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DIALOGUE_DOC_BATCH_SIZE = 5000
DATA_PATH = Path(__file__).parent.parent / "data"
DIALOGUE_DATA_PATH = DATA_PATH / "dialogue_data"
TEMPLATE_DATA_PATH = DATA_PATH / "character_templates"

# Check for GPU or mps
if torch.cuda.is_available():
    DEVICE = "cuda"
elif torch.backends.mps.is_available():
    DEVICE = "mps"
else:
    DEVICE = "cpu"


def main():
    """Process and load D&D dialogue and character template data into ChromaDB.

    This function performs the following operations:
    1. Creates or recreates ChromaDB collections for character dialogue and templates
    2. Loads dialogue data from JSON files in the dialogue_data directory
    3. Extracts character utterances (excluding DM dialogue) and stores them
    4. Loads character templates from cleaned template data
    5. Uses GPU acceleration for embeddings if available (CUDA or MPS)

    The function processes:
        - Dialogue data: Character speech from Critical Role episodes
        - Character templates: Pre-built D&D character stat blocks with metadata

    Collections created:
        - character_dialogue: Stores individual character utterances for dialogue style retrieval
        - character_templates: Stores character stat blocks with searchable summaries

    Side Effects:
        - Deletes existing collections if they exist
        - Creates new ChromaDB collections
        - Writes embeddings to ./chromadb directory
    """
    db = chromadb.PersistentClient(
        path="./chromadb",
    )
    try:
        db.delete_collection("character_dialogue")
        logger.info("Existing character_dialogue collection deleted.")
    except NotFoundError:
        pass
    try:
        db.delete_collection("character_templates")
        logger.info("Existing character_templates collection deleted.")
    except NotFoundError:
        pass
    if DEVICE in ["cuda", "mps"]:
        embedding_function = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2",
            device=DEVICE,
        )
    else:
        embedding_function = None
    # Create and populate dialogue collection
    dialogue_collection = db.create_collection(
        name="character_dialogue",
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"},
    )
    counter = 0
    dialogue_docs, dialogue_ids = [], []
    for json_file in tqdm(list(DIALOGUE_DATA_PATH.rglob("*.json"))):
        with open(json_file, "r", encoding="utf-8") as file:
            dialogue_data = json.load(file)
        for chunk in dialogue_data:
            for turn in chunk["TURNS"]:
                # Skip if Matt Mercer is the only speaker
                if turn["NAMES"] == "MATT":
                    continue
                dialogue_docs.append("".join(turn["UTTERANCES"]))
                dialogue_ids.append(f"{counter}")
                counter += 1
                if len(dialogue_docs) % DIALOGUE_DOC_BATCH_SIZE == 0:
                    dialogue_collection.add(
                        documents=dialogue_docs,
                        ids=dialogue_ids,
                    )
                    dialogue_docs, dialogue_ids = [], []
    if dialogue_docs:
        dialogue_collection.add(
            documents=dialogue_docs,
            ids=dialogue_ids,
        )

    logger.info("JSON dialogue extraction complete")

    # Create and populate template collection
    template_collection = db.create_collection(
        name="character_templates",
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"},
    )
    with open(
        TEMPLATE_DATA_PATH / "dnd_templates_cleaned.json",
        "r",
        encoding="utf-8",
    ) as file:
        template_data = json.load(file)

    for char_summary, char_template in template_data.items():
        template_collection.add(
            documents=[char_summary],
            metadatas=[char_template],
            ids=[char_template["hash"]],
        )

    logger.info("JSON unique character template extraction complete")


if __name__ == "__main__":
    main()
    print("Processing complete!")
