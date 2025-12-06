import os
import json
import logging
from datetime import datetime
from uuid import uuid4

import chromadb
from dotenv import load_dotenv
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)
from openai import OpenAI, AsyncOpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class NPCAgent:
    """Dungeons and Dragons NPC chat agent"""

    def __init__(self, description: str):
        self.db = db = chromadb.PersistentClient(
            path="./chromadb",
        )
        try:
            self.dialogue_collection = db.get_collection("character_dialogue")
        except Exception as e:
            logger.error(f"Dialogue collection not found: {e}")
            raise
        try:
            self.template_collection = db.get_collection("character_templates")
        except Exception as e:
            logger.error(f"Template collection not found: {e}")
            raise
        try:
            db.delete_collection("npc_memories")
            logger.info("Previous memories deleted!")
        except Exception as e:
            logger.info("No memories to delete!")
        self.memory_collection = db.create_collection(
            name="npc_memories",
            metadata={"hnsw:space": "cosine"},
        )
        self.sync_client = OpenAI(
            api_key=os.getenv("ASI_API_KEY"),
            base_url="https://inference.asicloud.cudos.org/v1",
        )
        self.async_client = AsyncOpenAI(
            api_key=os.getenv("ASI_API_KEY"),
            base_url="https://inference.asicloud.cudos.org/v1",
        )
        self.DEFAULT_SITUATION = "standing in your usual location"
        self.npc_name = None
        self.description = None
        self.character_template = None
        self.dialogue_style = None
        self.setup_from_description(description)
        self.uagent = Agent(
            name=self.npc_name,
            seed="npc_agent_seed",
            port=8001,
            mailbox=True,
        )
        self.setup_protocol()

    def _get_dialogue_style(
        self,
        personality: str,
        situation: str | None = None,
    ) -> list[str]:
        situation = situation or self.DEFAULT_SITUATION

        results = self.dialogue_collection.query(
            query_texts=[f"{personality} {situation}"],
            n_results=1,
        )
        if not results["documents"][0]:
            logger.warning(f"No dialogue style found for: {personality}")
            return ["speaks in a neutral manner"]
        return results["documents"][0]

    def _get_character_template(
        self,
        description: str,
        race: str = None,
        npc_class: str = None,
        level: int = None,
        background: str = None,
    ):
        template_list = []
        if race:
            template_list.append({"race": {"$eq": race}})
        if npc_class:
            template_list.append({"class": {"$eq": npc_class}})
        if level:
            template_list.append({"level": {"$eq": level}})
        if background:
            template_list.append({"background": {"$eq": background}})

        # where_dict = {"$and": template_list}
        results = self.template_collection.query(
            query_texts=[description],
            # where=where_dict if template_list else None,
            n_results=1,
        )
        if not results["metadatas"] or not results["metadatas"][0]:
            raise ValueError("No matching character template found")
        return results["metadatas"][0][0]

    def _store_npc_memory(
        self,
        interaction: str,
        npc_id: str,
    ) -> str:

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.memory_collection.add(
            documents=[interaction],
            metadatas=[{"npc_id": npc_id, "timestamp": timestamp}],
            ids=[f"{npc_id}_{timestamp}"],
        )
        return "stored"

    def _retrieve_npc_memory(
        self,
        context: str,
        npc_id: str,
    ):
        results = self.memory_collection.query(
            query_texts=[context],
            where={"npc_id": npc_id},
            n_results=1,
        )
        return results["documents"][0] if results["documents"] else []

    def setup_from_description(self, description: str):
        self.description = description
        response = self.sync_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": """Extract dungeons and dragons character info with these exact keys:
                {
                    "npc_name": "string",
                    "personality": "string (required)",
                    "situation": "string",
                    "race": "string",
                    "npc_class": "string",
                    "background": "string",
                    "level": "integer",
                }
                Only return valid JSON, no other text.""",
                },
                {"role": "user", "content": description},
            ],
        )
        try:
            structured_response = json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
        if "personality" not in structured_response:
            logger.warning(
                "LLM did not return 'personality'. Using default: neutral temperament"
            )
        # Call startup functions
        self.character_template = self._get_character_template(
            description,
            race=structured_response.get("race"),
            npc_class=structured_response.get("npc_class"),
            level=structured_response.get("level"),
            background=structured_response.get("background"),
        )
        self.dialogue_style = self._get_dialogue_style(
            structured_response.get("personality", "neutral temperament"),
            structured_response.get("situation"),
        )
        retrieved_npc_name = structured_response.get("npc_name")
        self.npc_name = retrieved_npc_name or "Gerald"

    def setup_protocol(self):
        """Set up uAgent chat protocol"""
        protocol = Protocol(spec=chat_protocol_spec)

        @protocol.on_message(ChatMessage)
        async def reply_to_message(ctx: Context, sender: str, message: ChatMessage):
            """Handle incoming chat messages and reply"""
            try:
                # Send acknowledgement
                await ctx.send(
                    sender,
                    ChatAcknowledgement(
                        timestamp=datetime.now(),
                        acknowledged_msg_id=message.msg_id,
                    ),
                )
                # Extract text from message
                user_text = ""
                for item in message.content:
                    if isinstance(item, TextContent):
                        user_text += item.text

                logger.info(f"Received message from: {sender}")

                # Generate response using RAG + LLM
                response = await self.generate_response(user_text)
                # Send response back to user
                await ctx.send(
                    sender,
                    ChatMessage(
                        timestamp=datetime.now(),
                        msg_id=uuid4(),
                        content=[TextContent(type="text", text=response)],
                    ),
                )
                logger.info(f"Sent NPC response to {sender}")
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                # Send error response
                await ctx.send(
                    sender,
                    ChatMessage(
                        timestamp=datetime.now(),
                        msg_id=uuid4(),
                        content=[
                            TextContent(
                                type="text",
                                text=f"Sorry, I encountered an error: {str(e)}",
                            ),
                        ],
                    ),
                )

        @protocol.on_message(ChatAcknowledgement)
        async def handle_acknowledgements(
            ctx: Context,
            sender: str,
            message: ChatAcknowledgement,
        ):
            """Handle chat acknowledgements"""
            logger.info(f"Received acknowledgement from: {sender}")

        # Add protocol to uAgent
        self.uagent.include(protocol, publish_manifest=True)

    async def generate_response(self, query: str) -> str:
        # Get character template
        character_template = self.character_template
        dialogue_style = self.dialogue_style
        retrieved_memories = self._retrieve_npc_memory(query, self.uagent.name)
        npc_memories = (
            retrieved_memories[0] if retrieved_memories else "First encounter."
        )
        memory_context = f"Previous interactions: {npc_memories}"
        system_content = f"""You are {self.npc_name}.
        Character: {character_template}
        Dialogue Style: {dialogue_style}
        Past Interactions: {memory_context}
        Respond in character to the player's message.
        """
        response = await self.async_client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": query},
            ],
        )
        npc_reply = response.choices[0].message.content
        if not npc_reply:
            logger.error("Empty response from LLM")
            return "I'm not sure how to respond..."
        self._store_npc_memory(
            f"Player: {query}\nYou: {npc_reply}",
            self.uagent.name,
        )
        return npc_reply

    def run(self):
        """Start uAgent"""
        logger.info("Starting NPC uAgent")
        logger.info(f"Agent address: {self.uagent.address}")
        self.uagent.run()


if __name__ == "__main__":
    test_description = (
        "Name: Gary, "
        "Personality: rude, "
        "Class: Fighter, "
        "Race: Dwarf, "
        "Situation: Hanging out in the tavern"
    )
    try:
        agent = NPCAgent(test_description)
        agent.run()
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
