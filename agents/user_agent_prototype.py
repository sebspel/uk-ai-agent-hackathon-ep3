"""User agent for interfacing with NPC agents"""

import asyncio
from typing import Literal

from uagents import Agent, Context, Model


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


# Shared state for response handling
response_queue = asyncio.Queue()


def create_user_agent(name: str = "player", port: int = 8001):
    """Create and configure a user agent"""
    agent = Agent(
        name=name,
        port=port,
        seed=f"{name}_seed",
    )

    @agent.on_message(NPCMessage)
    async def handle_npc_response(_ctx: Context, _sender: str, msg: NPCMessage):
        """Handle responses from NPC agent"""
        await response_queue.put(msg.text)

    return agent


async def setup_npc(agent: Agent, npc_address: str, description: str):
    """Send setup message to NPC agent"""
    ctx = agent._ctx if hasattr(agent, "_ctx") else None
    if ctx:
        await ctx.send(
            npc_address,
            SetupMessage(type="str", description=description),
        )


async def send_message_to_npc(
    agent: Agent, npc_address: str, message: str, timeout: float = 30.0
) -> str:
    """Send message to NPC and wait for response"""
    ctx = agent._ctx if hasattr(agent, "_ctx") else None
    if not ctx:
        return "Error: Agent context not available"

    # Clear the queue
    while not response_queue.empty():
        response_queue.get_nowait()

    # Send message
    await ctx.send(
        npc_address,
        PlayerMessage(type="str", text=message),
    )

    # Wait for response with timeout
    try:
        response = await asyncio.wait_for(response_queue.get(), timeout=timeout)
        return response
    except asyncio.TimeoutError:
        return "Error: Response timeout"
