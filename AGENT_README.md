# D&D NPC Chat Agent

## Overview
An intelligent Dungeons and Dragons NPC (Non-Player Character) that you can interact with through natural conversation. This agent brings tabletop RPG characters to life with dynamic dialogue, personality-driven responses, and even combat mechanics!

## What This Agent Does
This agent creates an immersive D&D NPC experience by:
- **Generating Dynamic Characters**: Creates unique NPCs from text descriptions with authentic D&D stats, abilities, and personality traits
- **Conversational AI**: Engages in natural dialogue that matches the character's personality and situation
- **Memory System**: Remembers past interactions to provide contextual, coherent conversations
- **Combat Mechanics**: Can engage in combat, track HP, and even attack back if provoked
- **RAG-Powered Responses**: Uses Retrieval Augmented Generation with Critical Role dialogue examples to generate authentic D&D-style conversations

## How to Use This Agent

### Basic Interaction
Simply chat with the NPC naturally! The agent will respond in character based on their personality, background, and your previous interactions.

**Example:**
```
You: Hello there, what brings you to this tavern?
NPC: *leans back in chair* Just passing through, friend. Looking for work if you've got any.
```

### Combat
Want to test your luck in combat? Include dice roll results in your message:

**Format:** "I attack you rolling a [HIT VALUE] to hit for [DAMAGE] damage"

**Example:**
```
You: I attack you rolling a 14 to hit for 4 damage
NPC: *staggers back* You dare strike me?! *draws weapon*
```

**Warning:** Deal enough damage and the NPC will die (permanently for that character instance). The NPC may also attack back depending on how you treat them!

### Tips for Best Results
- Be descriptive in your interactions
- Stay in character for a more immersive experience
- The NPC remembers your conversations, so your relationship develops over time
- Hostile actions may turn the NPC aggressive
- Each NPC has unique stats, abilities, and personality traits

## Character Features
Each NPC includes:
- **Name & Background**: Authentic D&D character identity
- **Stats & Abilities**: Hit points, class, race, level, and abilities
- **Personality**: Unique traits that shape dialogue and behavior
- **Dialogue Style**: Speech patterns based on Critical Role dialogue examples
- **Combat Capability**: Can engage in D&D-style combat encounters

## Technical Details
- Built on the fetch.ai uAgents framework
- Uses ChromaDB for Retrieval Augmented Generation (RAG)
- Powered by ASI-CLOUD inference (OpenAI GPT-OSS-20B)
- Persistent memory across conversations
- Combines character templates from D&D characters dataset with dialogue from Critical Role

## Notes
- This agent runs locally and requires the host script to stay active
- The agent's address and name are defined on initialization and are not linked
- NPCs can die if dealt fatal damage
- Memory is persistent for the character instance

## Attribution
Character templates sourced from the D&D Characters Dataset. Dialogue examples from the Critical Role Dataset (CRD3). Built for the fetch.ai Innovation Lab Hackathon Episode 3.

---

**Author:** Sebastian Sjostrom  
**Project Type:** Hackathon Innovation Lab Project  
**Framework:** fetch.ai uAgents
