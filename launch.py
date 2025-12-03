"""Launch both NPC agent and Gradio interface"""

import subprocess
import sys
import time


def main():
    """Start NPC agent and Gradio UI"""
    print("🚀 Starting NPC Chat System...")

    # Start NPC agent in background
    print("📡 Starting NPC Agent...")
    npc_process = subprocess.Popen(
        [sys.executable, "agents/npc_agent.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Give the agent time to initialize
    time.sleep(3)

    # Start Gradio interface
    print("🎨 Starting Gradio Interface...")
    try:
        subprocess.run([sys.executable, "ui/gradio_app.py"], check=False)
    finally:
        print("\n🛑 Shutting down NPC Agent...")
        npc_process.terminate()
        npc_process.wait()


if __name__ == "__main__":
    main()
