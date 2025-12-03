# uk-ai-agent-hackathon-ep3
UK AI Agent Hackathon EP3 by ASI submission repo

## 🎭 D&D NPC Chat System

An interactive chat interface for D&D NPCs powered by the uagents framework and Gradio.

## Features

- **AI-Powered NPCs**: Create custom D&D NPCs with personalities, backgrounds, and dialogue styles
- **Memory System**: NPCs remember past interactions using ChromaDB vector storage
- **Character Templates**: Retrieves appropriate character stats and templates
- **Dialogue Style Matching**: Finds similar dialogue patterns from a large corpus
- **Web Interface**: Beautiful Gradio-based chat UI for easy interaction

## Setup

1. **Install dependencies**:
   ```powershell
   python -m pip install -e .
   ```

2. **Set up environment variables**:
   Create a `.env` file with:
   ```
   ASI_API_KEY=your_asi_api_key_here
   ```

3. **Process character data** (first time only):
   ```powershell
   python scripts/process_data.py
   ```
   This creates the ChromaDB collections for dialogue and character templates.

## Usage

### Quick Start (Recommended)

Launch both the NPC agent and web interface:
```powershell
python launch.py
```

Then open your browser to `http://127.0.0.1:7860`

### Manual Start

If you prefer to run components separately:

1. **Start the NPC agent**:
   ```powershell
   python agents/npc_agent.py
   ```

2. **In a new terminal, start the Gradio UI**:
   ```powershell
   python ui/gradio_app.py
   ```

### Using the Interface

1. **Setup NPC**: Enter a description like "A gruff dwarf blacksmith, level 5 fighter with a folk hero background"
2. **Click Initialize NPC**: Wait for confirmation
3. **Start Chatting**: Type messages to interact with your NPC
4. **Context Aware**: The NPC remembers your conversation history

## Architecture

- `agents/npc_agent.py`: Main NPC agent using uagents framework
- `agents/user_agent.py`: User agent for sending messages to NPC
- `ui/gradio_app.py`: Gradio web interface
- `mcp_tools/server.py`: ChromaDB utilities for dialogue, templates, and memory
- `scripts/process_data.py`: Data processing pipeline for character data

## Requirements

- Python 3.13+
- ChromaDB for vector storage
- OpenAI-compatible API (ASI API)
- uagents framework for agent communication

