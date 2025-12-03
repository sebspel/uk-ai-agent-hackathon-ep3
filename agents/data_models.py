from typing import Literal

from uagents import Model


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
