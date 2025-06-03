#!/usr/bin/env python3
"""
Simple test script for conversational brainstorming functionality.

This script demonstrates the conversational flow where the brainstorming agent
asks follow-up questions and waits for user responses in the console.
"""

import os
import sys
from pathlib import Path

# Add the linkedin_ai_agent/src directory to Python path for imports
project_root = Path(__file__).parent
linkedin_src_path = project_root / "linkedin_ai_agent" / "src"
sys.path.insert(0, str(linkedin_src_path))

# Import environment variables
from dotenv import load_dotenv
load_dotenv()

# Import the crew
from linkedin_ai_agent.crew import LinkedinAiAgent

def main():
    """
    Test the conversational brainstorming functionality.
    This will demonstrate how the agent asks follow-up questions
    and waits for user responses before proceeding.
    """
    print("🚀 Starting Conversational Brainstorming Test")
    print("=" * 50)
    print("This test will demonstrate the agent asking follow-up questions")
    print("and waiting for your responses in a conversational flow.")
    print("=" * 50)
    
    try:
        # Get initial content idea from user
        print("\n💡 Let's start brainstorming your LinkedIn content!")
        initial_idea = input("What's your initial content idea? ")
        
        if not initial_idea.strip():
            initial_idea = "I want to write about my recent project experience"
            print(f"Using default idea: {initial_idea}")
        
        # Initialize the crew
        print("\n🔧 Initializing LinkedIn AI Agent crew...")
        crew_instance = LinkedinAiAgent()
        
        # Set up the inputs for the crew
        inputs = {
            'initial_idea': initial_idea,
            'user_writing_style': "Professional yet conversational, with personal insights and practical examples",
            'target_audience': "LinkedIn professionals and entrepreneurs",
            'content_goals': "Engage audience, share expertise, build personal brand"
        }
        
        print(f"\n🎯 Starting conversational brainstorming for: '{initial_idea}'")
        print("\n" + "="*60)
        print("🤖 The agent will now ask you follow-up questions.")
        print("💬 Please respond naturally - this is a conversation!")
        print("✨ The agent will continue until it has enough context.")
        print("="*60)
        
        # Run the crew - this should trigger conversational flow
        result = crew_instance.crew().kickoff(inputs=inputs)
        
        print("\n" + "="*60)
        print("🎉 Brainstorming conversation completed!")
        print("="*60)
        print("\n📝 Final brainstorming result:")
        print(result)
        
    except KeyboardInterrupt:
        print("\n\n👋 Conversation interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error during brainstorming: {str(e)}")
        print("💡 This might be due to missing API keys or configuration issues.")
        print("📖 Please check your .env file has the required API keys.")

if __name__ == "__main__":
    main() 