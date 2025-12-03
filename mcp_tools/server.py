"""MCP and utility tools"""

from datetime import datetime

import chromadb

# from mcp.server.fastmcp import FastMCP

DEFAULT_SITUATION = "standing in your usual location"
# mcp = FastMCP("NPC RAG")

db = chromadb.PersistentClient(
    path="./chromadb",
)
dialogue_collection = db.get_collection("character_dialogue")
template_collection = db.get_collection("character_templates")
memory_collection = db.get_or_create_collection(
    name="npc_memories",
    metadata={"hnsw:space": "cosine"},
)


def get_dialogue_style(
    personality: str,
    situation: str | None = None,
) -> list[str]:
    situation = situation or DEFAULT_SITUATION

    results = dialogue_collection.query(
        query_texts=[f"{personality} {situation}"],
        n_results=1,
    )
    return results["documents"][0]


def get_character_template(
    description: str,
    race: str = None,
    npc_class: str = None,
    level: int = None,
    background: str = None,
):
    where_dict = {}
    if race:
        where_dict["race"] = race
    if npc_class:
        where_dict["class"] = npc_class
    if level:
        where_dict["level"] = level
    if background:
        where_dict["background"] = background

    results = template_collection.query(
        query_texts=[description],
        where=where_dict if where_dict else None,
        n_results=1,
    )
    return results["metadatas"][0][0]


def store_npc_memory(
    interaction: str,
    npc_id: str,
) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    memory_collection.add(
        documents=[interaction],
        metadatas=[{"npc_id": npc_id, "timestamp": timestamp}],
        ids=[f"{npc_id}_{timestamp}"],
    )
    return "stored"


def retrieve_npc_memory(
    context: str,
    npc_id: str,
):
    results = memory_collection.query(
        query_texts=[context],
        where={"npc_id": npc_id},
        n_results=1,
    )
    return results["documents"][0] if results["documents"] else []


# if __name__ == "__main__":
#     # Initialise and run the server
#     mcp.run(transport="stdio")
