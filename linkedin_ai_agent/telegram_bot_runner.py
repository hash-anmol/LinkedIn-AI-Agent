#!/usr/bin/env python
"""
LinkedIn AI Agent - Telegram Bot Runner

Simple script to start the Telegram bot with proper environment setup.
Run this script after setting up your bot token.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path for imports (at the end to avoid shadowing)
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

def load_env_file():
     """Load environment variables from .env file if it exists."""
     env_file = Path(__file__).parent / ".env"
     if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' not in line:
                            print(f"⚠️  Warning: Malformed line {line_num} in .env file: {line}")
                            continue
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')  # Remove quotes if present
                        if key:
                            os.environ[key] = value
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
            return
        print("✅ Loaded environment variables from .env file")
     else:
         print("📝 No .env file found. Make sure TELEGRAM_BOT_TOKEN is set in environment.")

def main():
    """Start the Telegram bot."""
    print("🤖 LinkedIn AI Agent - Telegram Bot Launcher")
    print("=" * 50)
    
    # Load environment variables
    load_env_file()
    
    # Check for required token
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("❌ TELEGRAM_BOT_TOKEN not found!")
        print("\n📝 Setup Instructions:")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Copy your bot token")
        print("3. Create a .env file with: TELEGRAM_BOT_TOKEN=your_token_here")
        print("4. Or set environment variable: export TELEGRAM_BOT_TOKEN='your_token_here'")
        print("\n📄 Example .env file content:")
        print("TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here")
        print("BRAVE_API_KEY=your_brave_api_key_here")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        sys.exit(1)
    
    # Import and start the bot
    try:
        from linkedin_ai_agent.telegram_bot import main as bot_main
        bot_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and dependencies are installed.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 