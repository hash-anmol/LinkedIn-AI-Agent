#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
from linkedin_ai_agent.crew import LinkedinAiAgent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# LinkedIn AI Agent - 4-Agent Content Creation System
# This main file runs the intelligent content creation workflow

def run():
    """
    Run the LinkedIn AI Agent crew for content creation.
    
    This starts the 4-agent workflow:
    1. Brainstorming Agent: Conducts intelligent conversation with web research
    2. Hook Agent: Creates compelling LinkedIn hooks
    3. Structure Agent: Designs optimal post structure
    4. Content Writing Agent: Writes final post with perfect style matching
    """
    # Input configuration for the content creation workflow
    inputs = {
        # Primary input - the user's initial content idea
        'initial_idea': 'AI voice agents impacting workplace productivity',
        
        # Context variables for dynamic content
        'current_year': str(datetime.now().year),
        
        # Optional: Additional context that can be used in tasks
        'target_audience': 'Industry professionals and ambitious Gen-Z individuals',
        'content_focus': 'Tech and startups, India\'s development, AI advancements'
    }
    
    try:
        print("🚀 Starting LinkedIn AI Agent - 4-Agent Content Creation System")
        print(f"📝 Initial Content Idea: {inputs['initial_idea']}")
        print("=" * 60)
        
        # Execute the 4-agent workflow
        result = LinkedinAiAgent().crew().kickoff(inputs=inputs)
        
        print("=" * 60)
        print("✅ Content creation complete! Check 'linkedin_post.md' for your final post.")
        print("🎯 The post has been created with perfect style matching.")
        
        return result
        
    except Exception as e:
        print(f"❌ An error occurred while running the LinkedIn AI Agent crew: {e}")
        raise


def run_interactive():
    """
    Run the crew with interactive input from the user.
    This allows users to provide their own content ideas.
    """
    print("🎯 LinkedIn AI Agent - Interactive Content Creation")
    print("=" * 50)
    
    # Get user input for content idea
    initial_idea = input("What content idea would you like to develop for LinkedIn? ")
    
    if not initial_idea.strip():
        print("❌ Please provide a content idea to get started.")
        return
    
    inputs = {
        'initial_idea': initial_idea,
        'current_year': str(datetime.now().year),
        'target_audience': 'Industry professionals and ambitious Gen-Z individuals',
        'content_focus': 'Tech and startups, India\'s development, AI advancements'
    }
    
    try:
        print(f"\n🚀 Starting content creation for: {initial_idea}")
        print("=" * 60)
        
        result = LinkedinAiAgent().crew().kickoff(inputs=inputs)
        
        print("=" * 60)
        print("✅ Your LinkedIn post is ready! Check 'linkedin_post.md'")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during content creation: {e}")
        raise


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "initial_idea": "AI voice agents transforming workplace productivity",
        'current_year': str(datetime.now().year),
        'target_audience': 'Industry professionals and ambitious Gen-Z individuals'
    }
    
    try:
        LinkedinAiAgent().crew().train(
            n_iterations=int(sys.argv[1]), 
            filename=sys.argv[2], 
            inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        LinkedinAiAgent().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "initial_idea": "AI voice agents transforming workplace productivity",
        "current_year": str(datetime.now().year),
        'target_audience': 'Industry professionals and ambitious Gen-Z individuals'
    }
    
    try:
        LinkedinAiAgent().crew().test(
            n_iterations=int(sys.argv[1]), 
            eval_llm=sys.argv[2], 
            inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


# Command line interface
if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "interactive":
            run_interactive()
        elif command == "train":
            train()
        elif command == "replay":
            replay()
        elif command == "test":
            test()
        else:
            print("Unknown command. Available commands: interactive, train, replay, test")
    else:
        run()
