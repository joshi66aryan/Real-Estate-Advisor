"""
RE-101 Investment Advisory Crew
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from langchain_openai import ChatOpenAI
import os
import logging

from ..tools import get_financial_calculator
from .guardrails import (
    get_final_recommendation_guardrails,
)


@CrewBase
class InvestmentAdvisorCrew():
    """RE-101 Investment Advisory Crew with Safety Guardrails"""
    
    # CrewAI loads these YAML files relative to this module's package path.
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self):
        """Initialize the crew with tools"""
        # Runtime knobs to control token budget and iteration depth.
        self.agent_max_iter = self._get_int("CREW_AGENT_MAX_ITER", 4)
        self.max_output_tokens = self._get_int("OPENAI_MAX_OUTPUT_TOKENS", 600)

        # Shared LLM instance used by all agents.
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=self.max_output_tokens,
        )
        # Feature flags for memory and optional research tools.
        self.memory_enabled = os.getenv("CREW_MEMORY_ENABLED", "false").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        self.embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self.web_tools_enabled = self._is_enabled("CREW_WEB_TOOLS_ENABLED", default=True)
        self.scrape_tool_enabled = self._is_enabled(
            "CREW_SCRAPE_TOOL_ENABLED", default=False
        )
        
        # Tool inventory built once and reused by relevant agents.
        self.research_tools = self._build_research_tools()
        self.financial_calculator = get_financial_calculator()

    @staticmethod
    def _is_enabled(env_var_name: str, default: bool = False) -> bool:
        raw_value = os.getenv(env_var_name)
        if raw_value is None:
            return default
        return raw_value.strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _get_int(env_var_name: str, default: int) -> int:
        raw_value = os.getenv(env_var_name)
        if raw_value is None:
            return default
        try:
            return int(raw_value)
        except ValueError:
            return default

    def _build_research_tools(self) -> list:
        # Research tools are optional to keep execution robust when external APIs are unavailable.
        if not self.web_tools_enabled:
            logging.warning(
                "Web research tools disabled via CREW_WEB_TOOLS_ENABLED; proceeding without web tools."
            )
            return []

        tools = []

        # Primary external web search tool for finding current sources and URLs.
        if os.getenv("SERPER_API_KEY"):
            tools.append(SerperDevTool())

        # Optional direct page scraping support.
        if self.scrape_tool_enabled:
            tools.append(ScrapeWebsiteTool())

        if tools:
            return tools

        logging.warning(
            "No research tools enabled. Set SERPER_API_KEY for web search and/or "
            "CREW_SCRAPE_TOOL_ENABLED=true for website scraping."
        )
        return []
    
    @agent
    def data_integration_specialist(self) -> Agent:
        # Agent uses research tools when enabled; otherwise still operates from provided context.
        return Agent(
            config=self.agents_config['data_integration_specialist'],
            tools=self.research_tools,
            llm=self.llm,
            max_iter=self.agent_max_iter,
            verbose=False
        )
    
    @agent
    def financial_modeling_analyst(self) -> Agent:
        # Deterministic calculator tool keeps finance math consistent across runs.
        return Agent(
            config=self.agents_config['financial_modeling_analyst'],
            tools=[self.financial_calculator],
            llm=self.llm,
            max_iter=self.agent_max_iter,
            verbose=False
        )
    
    @agent
    def strategy_alignment_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config['strategy_alignment_advisor'],
            llm=self.llm,
            max_iter=self.agent_max_iter,
            verbose=False
        )
    
    @agent
    def investment_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config['investment_advisor'],
            tools=self.research_tools,
            llm=self.llm,
            max_iter=self.agent_max_iter,
            verbose=False
        )
    
    @task
    def data_integration_task(self) -> Task:
        return Task(
            config=self.tasks_config['data_integration_task'],
        )
    
    @task
    def financial_modeling_task(self) -> Task:
        return Task(
            config=self.tasks_config['financial_modeling_task'],
        )
    
    @task
    def strategy_alignment_task(self) -> Task:
        # This stage now handles both strategy fit and risk screening.
        return Task(
            config=self.tasks_config['strategy_alignment_task'],
        )
    
    @task
    def investment_advisory_task(self) -> Task:
        return Task(
            config=self.tasks_config['investment_advisory_task'],
            guardrails=get_final_recommendation_guardrails(),
            guardrail_max_retries=self._get_int("FINAL_GUARDRAIL_MAX_RETRIES", 5),
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the RE-101 Investment Advisory crew"""
        # Crew kwargs are assembled dynamically so optional features can be toggled safely via env vars.
        crew_kwargs = {
            "agents": self.agents,
            "tasks": self.tasks,
            "process": Process.sequential,
            "verbose": False,
            "memory": self.memory_enabled,
        }

        if self.memory_enabled:
            # Embedder is only attached when memory is enabled to avoid unnecessary provider calls.
            crew_kwargs["embedder"] = {
                "provider": "openai",
                "config": {
                    "model": self.embedding_model
                }
            }

        return Crew(
            **crew_kwargs
        )
