#!/usr/bin/env python
"""
LinkedIn AI Agent - Telegram Bot Integration

This module provides Telegram bot functionality for the LinkedIn AI Agent,
enabling users to interact with the 4-agent content creation workflow through chat.

Features:
- Interactive brainstorming through chat
- Progress tracking with status updates
- File delivery of final LinkedIn posts
- Error handling and user guidance
"""

import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from linkedin_ai_agent.crew import LinkedinAiAgent
from linkedin_ai_agent.main import run_interactive
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Configure logging for Telegram bot
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class LinkedInTelegramBot:
    """
    Telegram bot wrapper for LinkedIn AI Agent.
    
    Handles user interactions and manages the 4-agent content creation workflow
    through Telegram chat interface.
    """
    
    def __init__(self, token: str):
        """
        Initialize the Telegram bot with the provided token.
        
        Args:
            token (str): Telegram bot token from BotFather
        """
        self.token = token
        self.application = Application.builder().token(token).build()
        self.user_sessions: Dict[int, Dict[str, Any]] = {}  # Track user sessions
        
        # Set up bot handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up all Telegram bot command and message handlers."""
        # Command handlers for bot functionality
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("create", self.create_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("cancel", self.cancel_command))
        
        # Message handler for content ideas and general chat
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /start command - Welcome message and bot introduction.
        
        Explains bot capabilities and guides user on how to begin.
        """
        if not update.effective_user or not update.message:
            return
            
        user = update.effective_user
        user_id = user.id
        
        # Initialize user session
        self.user_sessions[user_id] = {
            'status': 'idle',
            'current_idea': None,
            'created_at': datetime.now()
        }
        
        welcome_message = f"""
🎯 **Welcome to LinkedIn AI Agent!** 

Hi {user.first_name}! I'm your intelligent LinkedIn content creation assistant.

**🚀 What I can do:**
• Transform your rough ideas into polished LinkedIn posts
• Conduct intelligent brainstorming with real-time web research
• Generate compelling hooks that grab attention
• Create optimal post structures
• Write content that matches your authentic style perfectly

**📝 How to get started:**
1. Send `/create` to start creating content
2. Or just send me your content idea directly!

**💡 Example ideas:**
• "AI voice agents impacting workplace"
• "India's startup ecosystem growth"
• "Future of remote work technology"

**🛠 Available Commands:**
/create - Start content creation
/status - Check current progress
/cancel - Cancel current session
/help - Show this help message

Ready to create amazing LinkedIn content? Let's go! 🚀
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command - Show detailed usage instructions."""
        if not update.message:
            return
        
        help_message = """
🤖 **LinkedIn AI Agent Help**

**🔄 The 4-Agent Workflow:**
1. **Brainstorming Agent** - Refines your idea with smart questions & research
2. **Hook Agent** - Creates compelling opening lines
3. **Structure Agent** - Designs optimal post layout
4. **Content Writer** - Writes final post matching your style

**💬 How to Use:**
• Send `/create` or just type your content idea
• Answer the brainstorming questions I ask
• I'll research relevant information automatically
• Review and approve the structure I create
• Receive your final LinkedIn post!

**⚡ Commands:**
/start - Welcome & introduction
/create - Begin content creation
/status - Check current progress
/cancel - Stop current session
/help - Show this help

**🎯 Tips for Better Results:**
• Be specific about your target audience
• Mention the impact you want to achieve
• Share any recent trends or data you're aware of
• Let me know your preferred posting style

Need help? Just ask me anything! 💪
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def create_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /create command - Start the content creation workflow."""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        # Initialize or reset user session
        self.user_sessions[user_id] = {
            'status': 'awaiting_idea',
            'current_idea': None,
            'created_at': datetime.now()
        }
        
        create_message = """
📝 **Let's Create Amazing LinkedIn Content!**

I'm ready to help you transform your idea into a compelling LinkedIn post.

**What's your content idea?** 

You can share:
• A topic you want to write about
• A trend you've noticed
• An insight you want to share
• A question you want to explore

**Examples:**
• "AI automation in healthcare"
• "Remote work productivity tips"
• "India's tech talent advantage"
• "Future of voice technology"

Just type your idea and I'll start the brainstorming process! 🧠✨
        """
        
        await update.message.reply_text(create_message, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command - Show current session status."""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions:
            await update.message.reply_text(
                "📊 **Status**: No active session\n\nSend `/create` to start creating content!",
                parse_mode='Markdown'
            )
            return
        
        session = self.user_sessions[user_id]
        status = session['status']
        
        status_messages = {
            'idle': "📊 **Status**: Ready to create\n\nSend `/create` to begin!",
            'awaiting_idea': "📊 **Status**: Waiting for your content idea\n\nJust type your idea to start!",
            'processing': "📊 **Status**: Creating your content\n\n🔄 The AI agents are working on your post...",
            'complete': "📊 **Status**: Content ready!\n\n✅ Your LinkedIn post has been delivered!"
        }
        
        message = status_messages.get(status, f"📊 **Status**: {status}")
        
        if session.get('current_idea'):
            message += f"\n\n💡 **Current Idea**: {session['current_idea']}"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command - Cancel current session."""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
            await update.message.reply_text(
                "❌ **Session Cancelled**\n\nYour current session has been cancelled. Send `/create` to start fresh!",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "📊 **No Active Session**\n\nNothing to cancel. Send `/create` to start creating content!",
                parse_mode='Markdown'
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle all text messages - Main content creation logic.
        
        Processes user content ideas and manages the 4-agent workflow.
        """
        if not update.effective_user or not update.message or not update.message.text:
            return
            
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        # Initialize session if it doesn't exist
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'status': 'awaiting_idea',
                'current_idea': None,
                'created_at': datetime.now()
            }
        
        session = self.user_sessions[user_id]
        
        # Handle content idea input
        if session['status'] in ['awaiting_idea', 'idle']:
            await self._process_content_idea(update, message_text)
        else:
            # General conversation or commands during processing
            await update.message.reply_text(
                "🔄 I'm currently processing your content. Please wait for the results!\n\nUse `/status` to check progress or `/cancel` to stop.",
                parse_mode='Markdown'
            )
    
    async def _process_content_idea(self, update: Update, content_idea: str):
        """
        Process the user's content idea through the 4-agent workflow.
        
        Args:
            update: Telegram update object
            content_idea: User's initial content idea
        """
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        # Update session status
        self.user_sessions[user_id]['status'] = 'processing'
        self.user_sessions[user_id]['current_idea'] = content_idea
        
        # Send initial confirmation
        await update.message.reply_text(
            f"🎯 **Great idea!** I'll help you create content about:\n*{content_idea}*\n\n🚀 Starting the 4-agent workflow...",
            parse_mode='Markdown'
        )
        
        try:
            # Send progress updates
            await update.message.reply_text(
                "🧠 **Brainstorming Agent**: Analyzing your idea and conducting research...",
                parse_mode='Markdown'
            )
            
            # Prepare inputs for the crew
            inputs = {
                'initial_idea': content_idea,
                'current_year': str(datetime.now().year),
                'target_audience': 'Industry professionals and ambitious Gen-Z individuals',
                'content_focus': 'Tech and startups, India\'s development, AI advancements'
            }
            
            # Execute the 4-agent workflow
            result = await self._run_crew_async(inputs, update)
            
            # Mark session as complete
            self.user_sessions[user_id]['status'] = 'complete'
            
            # Send final result
            await self._send_final_result(update, result, content_idea)
            
        except Exception as e:
            logger.error(f"Error processing content idea: {e}")
            await update.message.reply_text(
                f"❌ **Error**: Something went wrong during content creation.\n\n{str(e)}\n\nPlease try again with `/create`",
                parse_mode='Markdown'
            )
            
            # Reset session on error
            if user_id in self.user_sessions:
                self.user_sessions[user_id]['status'] = 'idle'
    
    async def _run_crew_async(self, inputs: Dict[str, Any], update: Update) -> Any:
        """
        Run the CrewAI workflow asynchronously with progress updates.
        
        Args:
            inputs: Input parameters for the crew
            update: Telegram update for sending progress messages
            
        Returns:
            Result from the crew execution
        """
        if not update.message:
            return None
            
        # This runs the crew in a separate thread to avoid blocking the bot
        def run_crew():
            return LinkedinAiAgent().crew().kickoff(inputs=inputs)
        
        # Send intermediate progress messages
        progress_messages = [
            "🎣 **Hook Agent**: Creating compelling opening lines...",
            "🏗 **Structure Agent**: Designing optimal post layout...", 
            "✍️ **Content Writer**: Writing your final LinkedIn post..."
        ]
        
        # Run crew asynchronously with progress updates
        import concurrent.futures
        import asyncio
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit the crew execution to thread pool
            future = executor.submit(run_crew)
            
            # Send progress messages while waiting
            for i, progress_msg in enumerate(progress_messages, 1):
                await asyncio.sleep(3)  # Wait a bit between messages
                if not future.done():
                    await update.message.reply_text(progress_msg, parse_mode='Markdown')
                await asyncio.sleep(2)  # Brief pause between agents
            
            # Wait for completion
            result = future.result()
            
        return result
    
    async def _send_final_result(self, update: Update, result: Any, original_idea: str):
        """
        Send the final LinkedIn post result to the user.
        
        Args:
            update: Telegram update object
            result: Result from crew execution
            original_idea: User's original content idea
        """
        if not update.effective_user or not update.message:
            return
            
        # Send completion message
        await update.message.reply_text(
            "✅ **Content Creation Complete!**\n\n🎉 Your LinkedIn post is ready!",
            parse_mode='Markdown'
        )
        
        # Format and send the final post
        final_post = f"""
🎯 **Your LinkedIn Post**
Original idea: {original_idea}

---

{str(result)}

---

📊 **Created by LinkedIn AI Agent**
🤖 4-Agent Workflow: Brainstorming → Hook → Structure → Content
        """
        
        await update.message.reply_text(final_post, parse_mode='Markdown')
        
        # Reset session for new content creation
        user_id = update.effective_user.id
        self.user_sessions[user_id]['status'] = 'idle'
        
        # Offer to create more content
        await update.message.reply_text(
            "🚀 **Ready for more?**\n\nSend `/create` or just type another idea to create more content!",
            parse_mode='Markdown'
        )
    
    def run(self):
        """Start the Telegram bot."""
        logger.info("🤖 LinkedIn AI Agent Telegram Bot starting...")
        self.application.run_polling()


def main():
    """
    Main function to start the Telegram bot.
    
    Requires TELEGRAM_BOT_TOKEN environment variable to be set.
    """
    # Get bot token from environment variable
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        print("📝 Please:")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Copy your bot token")
        print("3. Set the environment variable: export TELEGRAM_BOT_TOKEN='your_token_here'")
        print("4. Or create a .env file with: TELEGRAM_BOT_TOKEN=your_token_here")
        return
    
    # Create and start the bot
    bot = LinkedInTelegramBot(bot_token)
    print(f"🚀 LinkedIn AI Agent Telegram Bot is starting...")
    print(f"🔗 Find your bot at: https://t.me/{bot_token.split(':')[0]}")
    print("✅ Bot is running! Send /start to begin.")
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user.")
    except Exception as e:
        print(f"❌ Bot error: {e}")


if __name__ == "__main__":
    main() 