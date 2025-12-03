"""Simple test to verify the chat interface components work"""

import sys
import time


def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    try:
        import gradio

        print("✓ Gradio imported successfully")
    except ImportError as e:
        print(f"✗ Gradio import failed: {e}")
        return False

    try:
        from uagents import Agent, Bureau

        print("✓ uagents imported successfully")
    except ImportError as e:
        print(f"✗ uagents import failed: {e}")
        return False

    try:
        import chromadb

        print("✓ ChromaDB imported successfully")
    except ImportError as e:
        print(f"✗ ChromaDB import failed: {e}")
        return False

    try:
        from openai import AsyncOpenAI

        print("✓ OpenAI imported successfully")
    except ImportError as e:
        print(f"✗ OpenAI import failed: {e}")
        return False

    return True


def test_chromadb():
    """Test that ChromaDB has the required collections"""
    print("\nTesting ChromaDB collections...")
    try:
        import chromadb

        db = chromadb.PersistentClient(path="./chromadb")

        try:
            dialogue_collection = db.get_collection("character_dialogue")
            print(
                f"✓ character_dialogue collection found ({dialogue_collection.count()} items)"
            )
        except Exception as e:
            print(f"✗ character_dialogue collection not found: {e}")
            print("  Run 'python scripts/process_data.py' first!")
            return False

        try:
            template_collection = db.get_collection("character_templates")
            print(
                f"✓ character_templates collection found ({template_collection.count()} items)"
            )
        except Exception as e:
            print(f"✗ character_templates collection not found: {e}")
            print("  Run 'python scripts/process_data.py' first!")
            return False

        return True
    except Exception as e:
        print(f"✗ ChromaDB test failed: {e}")
        return False


def test_env():
    """Test that environment variables are set"""
    print("\nTesting environment variables...")
    import os
    from dotenv import load_dotenv

    load_dotenv()

    if os.getenv("ASI_API_KEY"):
        print("✓ ASI_API_KEY is set")
        return True
    else:
        print("✗ ASI_API_KEY not found in environment")
        print("  Create a .env file with ASI_API_KEY=your_key_here")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("NPC Chat Interface - System Check")
    print("=" * 60)

    all_passed = True

    if not test_imports():
        all_passed = False

    if not test_env():
        all_passed = False

    if not test_chromadb():
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! You can run the chat interface.")
        print("\nTo start:")
        print("  1. Terminal 1: python agents/npc_agent.py")
        print("  2. Terminal 2: python ui/gradio_app.py")
        print("  3. Open browser to http://127.0.0.1:7860")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1

    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
