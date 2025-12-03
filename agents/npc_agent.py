from dotenv import load_dotenv
import os
import json
from typing import Literal

from uagents import Agent, Context, Model

# from uagents_adapter import MCPServerAdapter

# from mcp_tools.server import mcp
from mcp_tools.server import (
    get_dialogue_style,
    get_character_template,
    store_npc_memory,
    retrieve_npc_memory,
)
from openai import AsyncOpenAI

load_dotenv()


class SetupMessage(Model):
    """Natural language user input"""

    type: Literal["str"]
    description: str


class PlayerMessage(Model):
    type: Literal["str"]
    text: str


class NPCMessage(Model):
    type: Literal["str"]
    text: str


client = AsyncOpenAI(
    api_key=os.environ["ASI_API_KEY"],
    base_url="https://api.asi1.ai/v1",
)
# # Create an MCP adapter with my MCP server
# mcp_adapter = MCPServerAdapter(
#     mcp_server=mcp,
#     asi1_api_key="YOUR ASI1 API KEY HERE",
#     model="asi1-mini",
# )

SEED_PHRASE = "folk_hero1"
npc = Agent(
    name="Gerald",
    seed=SEED_PHRASE,
    mailbox=True,
)


@npc.on_message(SetupMessage)
async def setup_npc(ctx: Context, sender: str, message: SetupMessage):
    startup_response = await client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": message.description}],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "setup_npc",
                    "description": "Extract Dungeons and Dragons character information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "npc_name": {"type": "string"},
                            "personality": {"type": "string"},
                            "situation": {"type": "string"},
                            "race": {"type": "string"},
                            "npc_class": {"type": "string"},
                            "background": {"type": "string"},
                            "level": {"type": "integer"},
                        },
                        "required": ["personality"],
                    },
                },
            }
        ],
        tool_choice={"type": "function", "function": {"name": "setup_npc"}},
    )
    structured_response = json.loads(
        startup_response.choices[0].message.tool_calls[0].function.arguments
    )
    # Call startup functions
    character_template = get_character_template(
        message.description,
        race=structured_response.get("race"),
        npc_class=structured_response.get("npc_class"),
        level=structured_response.get("level"),
        background=structured_response.get("background"),
    )
    dialogue_style = get_dialogue_style(
        structured_response["personality"],
        structured_response.get("situation"),
    )
    retrieved_npc_name = structured_response.get("npc_name")
    npc_name = retrieved_npc_name or npc.name
    ctx.storage.set("npc_name", npc_name)
    ctx.storage.set("character_template", character_template)
    ctx.storage.set("dialogue_style", dialogue_style)
    ctx.storage.set("player", sender)


@npc.on_message(PlayerMessage)
async def chat_with_player(ctx: Context, sender: str, message: PlayerMessage):
    # Get character template
    character_template = ctx.storage.get("character_template")
    dialogue_style = ctx.storage.get("dialogue_style")
    retrieved_memories = retrieve_npc_memory(message.text, npc.name)
    npc_memories = retrieved_memories[0] if retrieved_memories else "First encounter."
    memory_context = f"Previous interactions: {npc_memories}"
    system_content = f"""You are {ctx.storage.get("npc_name")}.
    Character: {character_template}
    Dialogue Style: {dialogue_style}
    Past Interactions: {memory_context}
    Respond in character to the player's message.
    """
    response = await client.chat.completions.create(
        model="asi1-mini",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": message.text},
        ],
    )
    npc_reply = response.choices[0].message.content
    store_npc_memory(
        f"Player: {message.text}\nYou: {npc_reply}",
        npc.name,
    )
    await ctx.send(sender, NPCMessage(text=npc_reply))


if __name__ == "__main__":
    npc.run()
