"""
LinkedIn AI Agent - Multi-Agent Content Creation System

This module defines the core crew structure for LinkedIn content creation
with style matching priority.
"""

from typing import List, Any, Optional
import warnings
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# CrewAI tools
from crewai_tools import SerperDevTool, WebsiteSearchTool

# Human input tool for conversational brainstorming
from linkedin_ai_agent.tools.human_input_tool import create_human_input_tool

# Try to import MCP tools, handle gracefully if not available
try:
    from mcpadapt import MCPServerAdapter
    MCP_AVAILABLE = True
    MCPServerAdapterType = MCPServerAdapter
except ImportError:
    print("🔍 MCP tools not available - using fallback search tools")
    MCPServerAdapterType = None
    MCP_AVAILABLE = False

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

@CrewBase
class LinkedinAiAgent():
    """
    LinkedIn AI Agent crew focused on conversational brainstorming only.
    
    This simplified version only uses the brainstorming agent for instant 
    conversational flow without delays.
    """

    def __init__(self, **kwargs):
        """Initialize the crew with only brainstorming capabilities"""
        super().__init__(**kwargs)
        
        # Initialize search tools
        self.search_tool = SerperDevTool()
        self.website_tool = WebsiteSearchTool()
        
        # Initialize human input tool for conversational brainstorming
        self.human_input_tool = create_human_input_tool(interface_type="console")
        
        # Set up Brave MCP tools if available
        self.brave_mcp_tools = None
        if MCP_AVAILABLE:
            try:
                # Check if Brave MCP server is available
                print("🔍 Checking for Brave MCP server availability...")
                self.brave_mcp_tools = None
            except Exception as e:
                print(f"🔍 Brave MCP not available, using fallback search tools: {e}")
                self.brave_mcp_tools = None

    def _get_search_tools(self):
        """Get the appropriate search tools - Brave MCP if available, otherwise fallback tools"""
        if self.brave_mcp_tools and MCPServerAdapterType:
            try:
                return MCPServerAdapterType(self.brave_mcp_tools)
            except Exception as e:
                print(f"❌ Error creating MCP adapter: {e}")
                print("   Falling back to traditional search tools.")
                return [self.search_tool, self.website_tool]
        else:
            return [self.search_tool, self.website_tool]

    def set_human_input_handler(self, handler_func):
        """Set a custom input handler for the human input tool (e.g., for Telegram integration)"""
        self.human_input_tool.set_input_handler(handler_func)

    # Only Brainstorming Agent - all others removed for instant responses
    @agent
    def brainstorming_agent(self) -> Agent:
        """Create brainstorming agent with conversational capabilities and web search"""
        
        # Combine human input tool with search tools
        agent_tools: List[Any] = [self.human_input_tool]
        
        # Add search tools (Brave MCP if available, otherwise fallback)
        if self.brave_mcp_tools and MCPServerAdapterType:
            try:
                with MCPServerAdapterType(self.brave_mcp_tools) as brave_tools:
                    agent_tools.extend(list(brave_tools))
                    print(f"🔍 Brainstorming agent using Brave MCP + Human Input with {len(agent_tools)} tools available")
            except Exception as e:
                print(f"❌ Error using Brave MCP tools: {e}")
                print("🔍 Brainstorming agent using fallback search tools + Human Input")
                agent_tools.extend([self.search_tool, self.website_tool])
        else:
            print("🔍 Brainstorming agent using fallback search tools + Human Input")
            agent_tools.extend([self.search_tool, self.website_tool])
        
        return Agent(
            config=self.agents_config['brainstorming_agent'], # type: ignore[index]
            verbose=True,
            tools=agent_tools,
            allow_delegation=False
        )

    # Only Brainstorming Task - all others removed
    @task
    def brainstorming_task(self) -> Task:
        return Task(
            config=self.tasks_config['brainstorming_task'], # type: ignore[index]
            agent=self.brainstorming_agent()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the LinkedIn AI Agent crew with only brainstorming agent for instant responses"""
        
        return Crew(
            agents=[
                self.brainstorming_agent()
                # All other agents removed for instant response mode
            ],
            tasks=[
                self.brainstorming_task()
                # All other tasks removed for instant response mode
            ],
            process=Process.sequential,
            verbose=True,
            memory=True,
        )
