![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3) ![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

# Dungeons and Dragons NPC AI Agent

## Author
Sebastian Sjostrom

## Introduction
This repository contains the code and instructions to setup your own locally ran Dungeons and Dragons NPC AI agent. The project focusses on a Dungeons and Dragons NPC agentic AI chat agent built on fetch.ai’s uAgents framework and ChromaDB for RAG. This is my first hackathon project and has been a whole lot of fun!

## Setup and launch
1. Install and setup uv with `pip install uv` and then `uv sync` to ensure the correct dependencies.
2. Ensure that you have a `.env` environment file in which the following 2 API keys are contained:
    - `ASI_API_KEY`: For ASI-CLOUD inference. Recommended for accessing the openi/gpt-oss-20b LLM although with minor modifications other inference providers can be used in place.
    - `AGENTVERSE_API_KEY`: For accessing the Asi1 and Agentverse ecosystems.
    
    Please also ensure you have the corresponding accounts setup that pair with these API keys.

3. Run the `process_data.py` file with `uv run process_data.py` to create the required dialogue and character template vector database. Note this will take a very long time on a CPU but around 5-10 minutes with an NVIDIA GPU or Apple MPS. If you would like to use a different, more comprehensive character template database JSON files may be easily slotted in in place of the default `dnd_templates_clean.json` file. Note that this and all preceding parts are a first time setup only and will not need to be repeated.

4. It's time to create your NPC! Run the agent script with `uv run -m agents.npc_agent`
5. Type your own custom D&D NPC description when prompted to bring the character to life.
6. Click on the agent inspector link and follow the instructions at the bottom of the page linked at: [uAgent Creation | Innovation Lab Resources](https://innovationlab.fetch.ai/resources/docs/agent-creation/uagent-creation#create-a-mailbox-in-agentverse)
7. Finally click agent profile or open your Agentverse agent tab and click 'Chat with Agent' to begin chatting!

## Usage notes
- Please keep your local script running to keep using the NPCAgent.
- The agent's address and name are defined on initialisation and so not linked.
- If you would like to attack the NPC please include the following structure in your prompt "… rolled a [YOUR HIT VALUE HERE] to hit for [DAMAGE ROLLED HERE] for best results. E.g. I attack you rolling a 14 to hit and 4 damage.
- If you deal enough damage to the NPC it will in fact, be dead (forever).
- The NPC may roll to attack your character depending on how it feels about you (and how you treat it).

## Attributions
This project uses the [Critical Role Dungeons and Dragons Dataset (CRD3)](https://github.com/RevanthRameshkumar/CRD3) for sourcing example dialogue extracts and the [D&D Characters Dataset](https://github.com/oganm/dnddata) compiled by Ogan Mancarci for character templates. Before running the agent some initial setup is required.
The class structure and protocol handling are adapted from the [Fetch.ai RAG agent example](https://github.com/fetchai/innovation-lab-examples/tree/main/Rag-agent/ango).
