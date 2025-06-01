from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool, WebsiteSearchTool, MCPServerAdapter
from mcp import StdioServerParameters
from typing import List
import os
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# LinkedIn AI Agent - 4-Agent Content Creation System
# Multi-agent crew for creating style-matched LinkedIn content with Brave MCP integration

@CrewBase
class LinkedinAiAgent():
    """LinkedIn AI Agent crew for intelligent content creation with perfect style matching and enhanced web search"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agent_config = "agents.yaml"
    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    def __init__(self):
        """Initialize the LinkedIn AI Agent with enhanced search capabilities"""
        super().__init__()
        
        # Set up Brave MCP tools for enhanced web search
        # This provides higher quality, independent search results vs traditional search APIs
        self.brave_mcp_tools = self._setup_brave_mcp_tools()
        
        # Fallback tools in case MCP is not available or configured
        self.search_tool = SerperDevTool()  # Backup search tool
        self.website_tool = WebsiteSearchTool()  # Website content analysis tool

    def _setup_brave_mcp_tools(self):
        """Set up Brave Search MCP server for enhanced web search capabilities"""
        try:
            # Check if BRAVE_API_KEY is available
            brave_api_key = os.getenv('BRAVE_API_KEY')
            if not brave_api_key:
                print("⚠️  BRAVE_API_KEY not found in environment variables.")
                print("   Falling back to SerperDevTool for web search.")
                return None
            
            # Configure Brave Search MCP server parameters
            # Uses stdio transport for local MCP server communication
            server_params = StdioServerParameters(
                command="npx",  # Run via npx (Node package executor)
                args=["@modelcontextprotocol/server-brave-search"],  # Official Brave MCP server
                env={"BRAVE_API_KEY": brave_api_key, **os.environ}  # Include API key and preserve other env vars
            )
            
            # Create MCP adapter with Brave Search server
            # This will be used as a context manager when creating agents
            print("✅ Brave MCP Search configured successfully!")
            print("   API Key: configured")
            return server_params
            
        except Exception as e:
            print(f"❌ Error setting up Brave MCP tools: {e}")
            print("   Falling back to SerperDevTool for web search.")
            return None

    def _get_search_tools(self):
        """Get the appropriate search tools - Brave MCP if available, otherwise fallback tools"""
        if self.brave_mcp_tools:
            # Return MCP adapter that will be used as context manager
            return MCPServerAdapter(self.brave_mcp_tools)
        else:
            # Return fallback tools
            return [self.search_tool, self.website_tool]

    # Agent 1: Enhanced Brainstorming Agent with Brave MCP integration
    @agent
    def brainstorming_agent(self) -> Agent:
        """Create brainstorming agent with enhanced Brave MCP web search capabilities"""
        
        # Use Brave MCP tools if available, otherwise fallback to traditional tools
        if self.brave_mcp_tools:
            # Use MCP context manager for Brave Search integration
            with MCPServerAdapter(self.brave_mcp_tools) as brave_tools:
                print(f"🔍 Brainstorming agent using Brave MCP with {len(brave_tools)} tools available")
                return Agent(
                    config=self.agents_config['brainstorming_agent'], # type: ignore[index]
                    verbose=True,
                    tools=list(brave_tools),  # Convert MCP tools to list for agent
                    allow_delegation=False  # This agent conducts the conversation directly
                )
        else:
            # Fallback to traditional search tools
            print("🔍 Brainstorming agent using fallback search tools (SerperDev + Website)")
            return Agent(
                config=self.agents_config['brainstorming_agent'], # type: ignore[index]
                verbose=True,
                tools=[self.search_tool, self.website_tool],  # Traditional web search integration
                allow_delegation=False  # This agent conducts the conversation directly
            )

    # Agent 2: Hook Generation Specialist
    @agent
    def hook_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['hook_agent'], # type: ignore[index]
            verbose=True,
            allow_delegation=False  # Specialized focus on hook creation
        )

    # Agent 3: Structure Architecture Specialist
    @agent
    def structure_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['structure_agent'], # type: ignore[index]
            verbose=True,
            allow_delegation=False  # Focused on structure design
        )

    # Agent 4: Content Writing Master
    @agent
    def content_writing_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['content_writing_agent'], # type: ignore[index]
            verbose=True,
            allow_delegation=False  # Final content creation with style matching
        )

    # Task 1: Enhanced Brainstorming with Brave MCP Web Research
    @task
    def brainstorming_task(self) -> Task:
        return Task(
            config=self.tasks_config['brainstorming_task'], # type: ignore[index]
            agent=self.brainstorming_agent()
        )

    # Task 2: Hook Generation Based on Brief
    @task
    def hook_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['hook_generation_task'], # type: ignore[index]
            agent=self.hook_agent(),
            context=[self.brainstorming_task()]  # Depends on brainstorming output
        )

    # Task 3: Structure Creation
    @task
    def structure_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['structure_generation_task'], # type: ignore[index]
            agent=self.structure_agent(),
            context=[self.brainstorming_task(), self.hook_generation_task()]  # Depends on previous outputs
        )

    # Task 4: Final Content Writing with Style Matching
    @task
    def content_writing_task(self) -> Task:
        return Task(
            config=self.tasks_config['content_writing_task'], # type: ignore[index]
            agent=self.content_writing_agent(),
            context=[self.brainstorming_task(), self.hook_generation_task(), self.structure_generation_task()],
            output_file='linkedin_post.md'  # Final output file
        )

    # # Legacy agents (keeping for reference)
    # @agent
    # def researcher(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['researcher'], # type: ignore[index]
    #         verbose=True
    #     )

    # @agent
    # def reporting_analyst(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['reporting_analyst'], # type: ignore[index]
    #         verbose=True
    #     )

    # # Legacy tasks (keeping for reference)
    # @task
    # def research_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['research_task'], # type: ignore[index]
    #     )

    # @task
    # def reporting_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['reporting_task'], # type: ignore[index]
    #         output_file='report.md'
    #     )

    @crew
    def crew(self) -> Crew:
        """Creates the LinkedIn AI Agent crew for intelligent content creation with enhanced search"""
        # 4-agent sequential workflow for LinkedIn content creation
        # Enhanced with Brave MCP for superior web search capabilities
        
        return Crew(
            agents=[
                self.brainstorming_agent(),
                self.hook_agent(),
                self.structure_agent(),
                self.content_writing_agent()
            ],
            tasks=[
                self.brainstorming_task(),
                self.hook_generation_task(),
                self.structure_generation_task(),
                self.content_writing_task()
            ],
            process=Process.sequential,  # Sequential execution for proper handoffs
            verbose=True,  # Show detailed output for transparency
            # Memory and context preservation across agents
            memory=True,  # Enable crew memory for better context retention
            # Style consistency is maintained through detailed task context and agent instructions
        )
