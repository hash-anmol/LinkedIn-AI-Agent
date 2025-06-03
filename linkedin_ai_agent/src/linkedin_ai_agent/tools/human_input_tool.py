from crewai.tools import BaseTool
from typing import Any, Dict, Optional, Callable
import asyncio
import threading
import time

# Optional telegram import - only needed if using Telegram interface
try:
    from telegram import Update
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    Update = None  # Type placeholder

class HumanInputTool(BaseTool):
    """
    A tool that allows agents to ask follow-up questions to humans
    and wait for responses in a conversational flow.
    """
    name: str = "Ask Human Follow-up Questions"
    description: str = (
        "Use this tool when you need to ask follow-up questions to gather more context "
        "from the user. This tool enables conversational interaction by asking specific "
        "questions and waiting for user responses. Use this tool multiple times to build "
        "a comprehensive understanding of the user's requirements."
    )
    
    def __init__(self, input_handler: Optional[Callable[[str], str]] = None, **kwargs):
        """
        Initialize the tool with an optional input handler for different interfaces.
        
        Args:
            input_handler: Function that handles getting input from user
                          (e.g., Telegram bot, CLI input, etc.)
        """
        super().__init__(**kwargs)
        # Store as private attributes to avoid field conflicts
        self._input_handler = input_handler or self._default_input_handler
        self._conversation_history = []
        self._response_cache = {}  # Cache for quick responses
        self._last_question_time = None
    
    def _default_input_handler(self, question: str) -> str:
        """
        Default input handler using console input.
        This will be overridden when using with Telegram or other interfaces.
        """
        print(f"\n🤔 Agent Question: {question}")
        response = input("Your response: ")
        return response
    
    def _run(self, question: str) -> str:
        """
        Ask a follow-up question to the human and return their response.
        
        Args:
            question: The question to ask the human
            
        Returns:
            The human's response to the question
        """
        try:
            # Track timing for performance monitoring
            start_time = time.time()
            
            # Store the question in conversation history
            self._conversation_history.append({
                "type": "agent_question",
                "content": question,
                "timestamp": start_time
            })
            
            # Check if we have a cached response (for testing/demo)
            if question in self._response_cache:
                cached_response = self._response_cache[question]
                self._conversation_history.append({
                    "type": "human_response", 
                    "content": cached_response,
                    "timestamp": time.time(),
                    "response_time": 0.1  # Simulated instant response
                })
                return cached_response
            
            # Get response from human using the input handler
            human_response = self._input_handler(question)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Store the human response in conversation history
            self._conversation_history.append({
                "type": "human_response", 
                "content": human_response,
                "timestamp": time.time(),
                "response_time": response_time
            })
            
            # If response took too long, suggest shorter timeout
            if response_time > 30:
                print(f"⚡ Response time: {response_time:.1f}s - Consider shorter timeouts for better UX")
            
            return human_response
            
        except Exception as e:
            error_msg = f"Error getting human input: {str(e)}"
            print(f"❌ {error_msg}")
            # Return a quick default to keep conversation flowing
            return "Let's move forward with the next question."
    
    def set_input_handler(self, handler: Callable[[str], str]):
        """Set a custom input handler"""
        self._input_handler = handler
    
    def get_conversation_history(self) -> list:
        """Return the full conversation history"""
        return self._conversation_history
    
    def clear_conversation_history(self):
        """Clear the conversation history"""
        self._conversation_history = []
    
    def set_response_cache(self, cache: Dict[str, str]):
        """Set cached responses for common questions (useful for demos)"""
        self._response_cache = cache
    
    def get_average_response_time(self) -> float:
        """Get average response time from conversation history"""
        response_times = [
            entry.get('response_time', 0) 
            for entry in self._conversation_history 
            if entry['type'] == 'human_response' and 'response_time' in entry
        ]
        return sum(response_times) / len(response_times) if response_times else 0


class TelegramHumanInputTool(HumanInputTool):
    """
    Specialized version of HumanInputTool for Telegram bot integration.
    This handles the async nature of Telegram bot responses.
    Note: Only available if telegram package is installed.
    """
    
    def __init__(self, telegram_bot=None, **kwargs):
        """
        Initialize with Telegram bot instance for handling responses.
        
        Args:
            telegram_bot: Instance of the Telegram bot for sending/receiving messages
        """
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot package is required for TelegramHumanInputTool")
        
        super().__init__(**kwargs)
        self._telegram_bot = telegram_bot
        self._pending_response = None
        self._response_received = False
        
    def set_telegram_handler(self, handler_func):
        """Set the Telegram message handler function"""
        self._input_handler = handler_func
    
    async def _telegram_input_handler(self, question: str, update: Optional[Any] = None) -> str:
        """
        Handle input through Telegram bot interface.
        This will send the question and wait for user response.
        """
        if not self._telegram_bot or not update:
            return "Telegram bot not available for conversation."
        
        try:
            # Check if update has message and reply_text method
            if hasattr(update, 'message') and update.message and hasattr(update.message, 'reply_text'):
                # Send the question to user via Telegram
                await update.message.reply_text(
                    f"🤔 **Follow-up Question:**\n\n{question}\n\n💬 Please share your thoughts:",
                    parse_mode='Markdown'
                )
            else:
                return "Invalid update object for Telegram conversation."
            
            # This would need integration with the bot's message handling
            # to wait for the next user message as response
            return "Response will be handled by Telegram bot message handler"
            
        except Exception as e:
            return f"Error sending question via Telegram: {str(e)}"


# Factory function to create the appropriate tool based on interface
def create_human_input_tool(interface_type="console", **kwargs):
    """
    Factory function to create the appropriate HumanInputTool based on interface.
    
    Args:
        interface_type: Type of interface ("console", "telegram", etc.)
        **kwargs: Additional arguments for tool initialization
        
    Returns:
        Configured HumanInputTool instance
    """
    if interface_type == "telegram":
        if not TELEGRAM_AVAILABLE:
            print("⚠️ Warning: Telegram not available, falling back to console interface")
            return HumanInputTool(**kwargs)
        return TelegramHumanInputTool(**kwargs)
    else:
        return HumanInputTool(**kwargs) 