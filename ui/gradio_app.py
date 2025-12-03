"""Gradio chat interface for NPC interaction"""

import asyncio
import threading

import gradio as gr
from dotenv import load_dotenv
from uagents import Bureau

from agents.user_agent import (
    create_user_agent,
    send_message_to_npc,
    setup_npc,
)

load_dotenv()


class NPCChatInterface:
    """Gradio-based chat interface for interacting with NPC agents"""

    def __init__(self):
        self.user_agent = None
        self.bureau = None
        self.npc_address = None
        self.npc_initialized = False
        self.chat_history = []

    def initialize_agents(self):
        """Initialize the user agent in a background thread"""
        if self.user_agent is None:
            self.user_agent = create_user_agent(name="player", port=8001)
            self.bureau = Bureau()
            self.bureau.add(self.user_agent)

            def run_bureau():
                self.bureau.run()

            agent_thread = threading.Thread(target=run_bureau, daemon=True)
            agent_thread.start()

            # Give agents time to start
            import time

            time.sleep(2)

    async def setup_npc_async(self, description: str, npc_address: str):
        """Setup the NPC with the given description"""
        if not self.user_agent:
            return "Error: User agent not initialized"

        if not npc_address:
            # Default NPC address from npc_agent.py
            npc_address = (
                "agent1qfpqn9jhvp9kcrktd7j93tdzr6f36h8ge5uz3f6hr8yqxr20qanv3hqjcx"
            )

        self.npc_address = npc_address
        await setup_npc(self.user_agent, npc_address, description)
        self.npc_initialized = True
        return f"✓ NPC setup complete!\n📍 NPC Address: {npc_address}\n📝 Description: {description}"

    def setup_npc_sync(self, description: str, npc_address: str):
        """Sync wrapper for NPC setup"""
        self.initialize_agents()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.setup_npc_async(description, npc_address)
            )
        finally:
            loop.close()

    async def send_message_async(self, message: str):
        """Send a message to the NPC"""
        if not self.npc_initialized or not self.npc_address:
            return "Please setup the NPC first!"

        response = await send_message_to_npc(self.user_agent, self.npc_address, message)
        return response

    def send_message(self, message: str, history: list):
        """Send message and update chat history"""
        if not message.strip():
            return history, ""

        if not self.npc_initialized:
            history.append((message, "⚠️ Please setup the NPC first!"))
            return history, ""

        # Add user message to history
        history.append((message, None))

        # Get response from NPC
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(self.send_message_async(message))
            # Update with NPC response
            history[-1] = (message, response)
        except Exception as err:  # noqa: BLE001
            history[-1] = (message, f"Error: {err!s}")
        finally:
            loop.close()

        return history, ""

    def create_interface(self):
        """Create the Gradio interface"""
        with gr.Blocks(title="NPC Chat Interface", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 🎭 D&D NPC Chat Interface")
            gr.Markdown("Interact with AI-powered D&D NPCs using the uagents framework")

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 🎲 NPC Setup")
                    npc_description = gr.Textbox(
                        label="NPC Description",
                        placeholder="e.g., A gruff dwarf blacksmith, level 5 fighter with a folk hero background",
                        lines=3,
                        value="A wise old wizard, level 10, with a sage background",
                    )
                    npc_address = gr.Textbox(
                        label="NPC Agent Address (optional)",
                        placeholder="Leave empty for default NPC",
                        value="",
                    )
                    setup_btn = gr.Button("🎯 Initialize NPC", variant="primary")
                    setup_status = gr.Textbox(
                        label="Setup Status", interactive=False, lines=3
                    )

                    gr.Markdown("### 📝 Instructions")
                    gr.Markdown(
                        """
                    1. **Setup NPC**: Describe your NPC character
                    2. **Start Chatting**: Interact with the NPC below
                    3. **Context Aware**: NPC remembers past interactions
                    
                    **Note**: Make sure the NPC agent is running first!
                    ```
                    python agents/npc_agent.py
                    ```
                    """
                    )

                with gr.Column(scale=2):
                    gr.Markdown("### 💬 Chat with NPC")
                    chatbot = gr.Chatbot(
                        label="Conversation",
                        height=500,
                        show_copy_button=True,
                    )
                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="Your Message",
                            placeholder="Type your message to the NPC...",
                            scale=4,
                        )
                        send_btn = gr.Button("Send", variant="primary", scale=1)

                    clear_btn = gr.Button("Clear Chat")

            # Event handlers
            setup_btn.click(
                fn=self.setup_npc_sync,
                inputs=[npc_description, npc_address],
                outputs=setup_status,
            )

            msg_input.submit(
                fn=self.send_message,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input],
            )

            send_btn.click(
                fn=self.send_message,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input],
            )

            clear_btn.click(fn=lambda: [], outputs=chatbot)

        return demo


def main():
    """Launch the Gradio interface"""
    interface = NPCChatInterface()
    demo = interface.create_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
    )


if __name__ == "__main__":
    main()
