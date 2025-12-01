from typing import Literal

from uagents import Agent, Context, Model
import httpx

class SetupMessage(Model):
    description: str
    race: str = None
    npc_class: str = None
    level: int = None
    background: str = None

class PlayerMessage(Model):
    type: Literal["str"]
    text: str


class NPCMessage(Model):
    type: Literal["str"]
    text: str

SEED_PHRASE = "folk_hero1"
npc = Agent(
    name="Gerald",
    seed=SEED_PHRASE,
    mailbox=True,
)
@npc.on_message(SetupMessage)
async def setup_npc(ctx: Context, sender: str, message: SetupMessage):
    async with httpx.AsyncClient() as client:
        template_response = await client.post(
            "http://localhost:8000/get_character_template",
            json={
                "description": message.description,
                "race": message.race,
                "npc_class": message.npc_class,
                "level": message.level,
                "background": message.background
            }
        )
        ctx.storage.set("character_template", template_response.json())
        ctx.storage.set("player", sender)
        await ctx.send(sender, NPCMessage(text=f"Finally, I the one and only {npc.name}, am alive!"))
@npc.on_message(PlayerMessage)
async def chat(ctx: Context, sender: str, message: PlayerMessage | NPCMessage):


