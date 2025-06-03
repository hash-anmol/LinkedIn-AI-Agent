#!/usr/bin/env python
"""
LinkedIn AI Agent - Telegram Bot Runner

Simple script to start the Telegram bot with conversational brainstorming.
Requires TELEGRAM_BOT_TOKEN environment variable to be set.
"""

import sys
import os

# Add the src directory to Python path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'linkedin_ai_agent', 'src')
sys.path.insert(0, src_path)

from linkedin_ai_agent.telegram_bot import main

if __name__ == "__main__":
    main() 