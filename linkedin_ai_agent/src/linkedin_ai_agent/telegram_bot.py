#!/usr/bin/env python
"""
LinkedIn AI Agent - Telegram Bot Integration

This module provides Telegram bot functionality for the LinkedIn AI Agent,
enabling users to interact with the conversational brainstorming workflow through chat.

Features:
- Interactive conversational brainstorming through chat
- Real-time question and response flow
- Progress tracking with status updates
- Style-matched content generation
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
    Telegram bot wrapper for LinkedIn AI Agent with instant conversational brainstorming.
    
    Handles user interactions with immediate responses - no delays, just like a real chatbot.
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
        
        # Conversation context for each user
        self.conversation_context: Dict[int, Dict[str, Any]] = {}
        
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
        self.application.add_handler(CommandHandler("summary", self.summary_command))
        
        # Message handler for instant conversation
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_instant_message)
        )
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - Welcome message and bot introduction."""
        if not update.effective_user or not update.message:
            return
            
        user = update.effective_user
        user_id = user.id
        
        # Initialize user session
        self.user_sessions[user_id] = {
            'status': 'ready',
            'questions_asked': 0,
            'context_gathered': {},
            'created_at': datetime.now()
        }
        
        self.conversation_context[user_id] = {
            'initial_idea': None,
            'questions_asked': [],
            'responses_given': [],
            'focus_areas_covered': set(),
            'user_writing_style': {},
            'conversation_flow': []
        }
        
        welcome_message = f"""
🚀 **Welcome to LinkedIn AI Agent!** 

Hi {user.first_name}! I'm your instant LinkedIn brainstorming assistant.

💡 **How I work:**
• Just send me your content idea and I'll start asking questions immediately
• Every message gets an instant response - no waiting!
• I'll help refine your idea through smart questions
• When we have enough context, I'll create your LinkedIn post

📝 **Ready to start?**
Just type your content idea and we'll begin brainstorming instantly!

Example: "AI voice agents changing workplace productivity"
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def create_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /create command - Start fresh conversation."""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        # Reset conversation
        self.user_sessions[user_id] = {
            'status': 'ready',
            'questions_asked': 0,
            'context_gathered': {},
            'created_at': datetime.now()
        }
        
        self.conversation_context[user_id] = {
            'initial_idea': None,
            'questions_asked': [],
            'responses_given': [],
            'focus_areas_covered': set(),
            'user_writing_style': {},
            'conversation_flow': []
        }
        
        await update.message.reply_text(
            "🎯 **Fresh start!** What's your LinkedIn content idea?",
            parse_mode='Markdown'
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command - Show current conversation status."""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions:
            await update.message.reply_text("💭 No active conversation. Just send me your idea to start!")
            return
        
        session = self.user_sessions[user_id]
        context_data = self.conversation_context.get(user_id, {})
        
        status_text = f"""
📊 **Conversation Status:**

💡 **Idea**: {context_data.get('initial_idea', 'Not set')}
❓ **Questions Asked**: {session['questions_asked']}
📝 **Areas Covered**: {len(context_data.get('focus_areas_covered', set()))}
🎯 **Status**: {session['status']}

Ready for your next message! 🚀
        """
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command - Reset conversation."""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        # Clear all session data
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        if user_id in self.conversation_context:
            del self.conversation_context[user_id]
        
        await update.message.reply_text(
            "🔄 **Conversation reset!** Send me a new idea to start fresh.",
            parse_mode='Markdown'
        )
    
    async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /summary command - Generate final content based on conversation."""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if user_id not in self.conversation_context or not self.conversation_context[user_id].get('initial_idea'):
            await update.message.reply_text("❌ No conversation to summarize. Start by sharing your content idea!")
            return
        
        await update.message.reply_text("✨ **Creating your LinkedIn post...**")
        
        # Generate final content
        try:
            final_content = await self._generate_final_content(user_id)
            await update.message.reply_text(f"🎉 **Your LinkedIn Post:**\n\n{final_content}")
        except Exception as e:
            logger.error(f"Error generating final content: {e}")
            await update.message.reply_text("❌ Error creating content. Try /create to start fresh.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command - Show help information."""
        if not update.message:
            return
        
        help_text = """
🤖 **LinkedIn AI Agent Help**

**💬 How to use:**
• Just send your content idea - I respond instantly!
• Answer my questions naturally
• Use /summary when ready to create your post

**⚡ Commands:**
/start - Welcome & introduction
/create - Start fresh conversation
/status - Check conversation progress
/summary - Generate LinkedIn post
/cancel - Reset conversation
/help - Show this help

**🎯 Tips:**
• Be conversational - I'll match your style
• Share personal experiences when relevant
• Be specific about your target audience

Ready to brainstorm? Just send your idea! 🚀
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def handle_instant_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle all text messages with instant responses - the core chatbot functionality.
        
        This method responds immediately to every user message like a real chatbot.
        """
        if not update.effective_user or not update.message or not update.message.text:
            return
            
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        logger.info(f"Instant message from user {user_id}: {message_text[:50]}...")
        
        # Initialize session if needed
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'status': 'ready',
                'questions_asked': 0,
                'context_gathered': {},
                'created_at': datetime.now()
            }
            self.conversation_context[user_id] = {
                'initial_idea': None,
                'questions_asked': [],
                'responses_given': [],
                'focus_areas_covered': set(),
                'user_writing_style': {},
                'conversation_flow': []
            }
        
        # Store user message in conversation flow
        self.conversation_context[user_id]['conversation_flow'].append({
            'type': 'user',
            'content': message_text,
            'timestamp': datetime.now()
        })
        
        # Generate instant response based on conversation context
        response = await self._generate_instant_response(user_id, message_text)
        
        # Store bot response in conversation flow
        self.conversation_context[user_id]['conversation_flow'].append({
            'type': 'bot',
            'content': response,
            'timestamp': datetime.now()
        })
        
        # Send instant response
        await update.message.reply_text(response, parse_mode='Markdown')
        
        logger.info(f"Instant response sent to user {user_id}")
    
    async def _generate_instant_response(self, user_id: int, user_message: str) -> str:
        """
        Generate an instant response based on conversation context.
        This is the core logic that makes the bot respond like a real chatbot.
        """
        session = self.user_sessions[user_id]
        context = self.conversation_context[user_id]
        
        # If this is the first message, treat it as the initial idea
        if not context['initial_idea']:
            context['initial_idea'] = user_message
            session['status'] = 'brainstorming'
            
            # Analyze the idea and ask the first strategic question
            return await self._ask_strategic_question(user_id, is_first=True)
        
        # Store the response and analyze writing style
        context['responses_given'].append(user_message)
        self._analyze_writing_style(user_id, user_message)
        
        # Determine what to ask next based on context
        return await self._ask_strategic_question(user_id, is_first=False)
    
    async def _ask_strategic_question(self, user_id: int, is_first: bool = False) -> str:
        """Ask the next strategic question based on conversation context."""
        session = self.user_sessions[user_id]
        context = self.conversation_context[user_id]
        
        if is_first:
            # First question - about target audience
            context['focus_areas_covered'].add('initial_idea')
            session['questions_asked'] += 1
            question = f"Got it! So you want to write about {context['initial_idea']}. Who's your target audience for this post?"
            context['questions_asked'].append(question)
            return question
        
        # Determine next question based on what we haven't covered yet
        areas_needed = {
            'audience': "Who exactly are you trying to reach?",
            'hook_style': "What kind of hook grabs you - bold statement or thought-provoking question?", 
            'personal_story': "Got any personal experience with this topic?",
            'unique_angle': "What's your unique take on this?",
            'key_message': "What's the main message you want to get across?",
            'writing_style': "How do you usually write - formal or conversational?"
        }
        
        # Find next area to cover
        for area, question in areas_needed.items():
            if area not in context['focus_areas_covered']:
                context['focus_areas_covered'].add(area)
                session['questions_asked'] += 1
                context['questions_asked'].append(question)
                return question
        
        # If we've covered all areas, suggest creating the post
        if session['questions_asked'] >= 4:
            return "Perfect! I think I have enough context. Ready to create your LinkedIn post? Type /summary to generate it! 🚀"
        
        # Fallback question
        return "Tell me more about what you want to achieve with this post?"
    
    def _analyze_writing_style(self, user_id: int, message: str):
        """Analyze and store user's writing style from their messages."""
        context = self.conversation_context[user_id]
        
        # Simple style analysis
        style_indicators = {
            'tone': 'conversational' if any(word in message.lower() for word in ['yeah', 'like', 'kinda', 'gonna']) else 'professional',
            'length': 'concise' if len(message.split()) < 20 else 'detailed',
            'enthusiasm': 'high' if any(punct in message for punct in ['!', '?', '...']) else 'moderate',
            'formality': 'casual' if any(word in message.lower() for word in ['hey', 'cool', 'awesome', 'great']) else 'formal'
        }
        
        context['user_writing_style'].update(style_indicators)
    
    async def _generate_final_content(self, user_id: int) -> str:
        """Generate final LinkedIn content based on conversation context."""
        context = self.conversation_context[user_id]
        
        # Build a comprehensive brief from conversation
        conversation_summary = []
        for entry in context['conversation_flow']:
            if entry['type'] == 'user':
                conversation_summary.append(f"User: {entry['content']}")
            else:
                conversation_summary.append(f"Agent: {entry['content']}")
        
        # Create a simple content structure based on gathered context
        content_parts = []
        
        # Hook (based on conversation)
        if context['initial_idea']:
            content_parts.append(f"🚀 {context['initial_idea']}")
        
        # Main content based on responses
        if context['responses_given']:
            key_points = context['responses_given'][:3]  # Use first 3 responses as key points
            for i, point in enumerate(key_points, 1):
                content_parts.append(f"\n{i}. {point}")
        
        # Call to action
        content_parts.append(f"\nWhat's your take on this? Let me know in the comments! 👇")
        
        return "\n".join(content_parts)
    
    def run(self):
        """Start the Telegram bot."""
        logger.info("🤖 LinkedIn AI Agent Telegram Bot starting...")
        logger.info("⚡ Instant response mode enabled - no delays!")
        
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
    print(f"⚡ INSTANT RESPONSE MODE - No delays, pure chatbot experience!")
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