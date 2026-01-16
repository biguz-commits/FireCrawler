from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, tool
from crewai.agents.agent_builder.base_agent import BaseAgent

from app.services.crew.local_llm import get_client
from app.services.crew.tools.html_tool import HtmlTool
from app.services.crew.tools.search_tool import BraveSearchTool
from app.services.crew.tools.similarity_research_tool import SimilarityResearchTool

llm = get_client()


@CrewBase
class ResearchCrew:
    """RAG-first research crew with review and web fallback"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @tool
    def similarity_research_tool(self):
        return SimilarityResearchTool()

    @tool
    def html_tool(self):
        return HtmlTool()

    @tool
    def search_tool(self):
        return BraveSearchTool()


    @agent
    def vector_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['vector_researcher'],  # type: ignore[index]
            verbose=True,
            tools=[
                self.similarity_research_tool()
            ],
            llm = llm
        )

    @agent
    def reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['reviewer'],  # type: ignore[index]
            verbose=True,
            llm = llm
        )

    @agent
    def web_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['web_researcher'],  # type: ignore[index]
            verbose=True,
            tools=[
                self.search_tool(),
                self.html_tool(),
            ],
            llm=llm
        )


    @task
    def vector_search_task(self) -> Task:
        return Task(
            config=self.tasks_config['vector_search_task']  # type: ignore[index]
        )

    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_task'],  # type: ignore[index]
        )

    @task
    def web_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['web_research_task'],  # type: ignore[index]
        )


    @crew
    def crew(self) -> Crew:
        """Creates the research crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=True,
            verbose=True
        )
