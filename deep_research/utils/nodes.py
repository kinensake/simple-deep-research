from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Send
from pydantic import BaseModel, Field

from deep_research.utils.state import DeepResearchState, SectionResearchState
from deep_research.utils.tools import search_tool
from deep_research.utils.prompt import (
    research_planner_instruction,
    research_writer_intruction,
    section_research_instruction,
)

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", max_tokens=20000)


class ResearchPlannerOutput(BaseModel):
    """Research Planner Output"""

    sections: List[str] = Field(..., description="List of sections to research")


def research_planner(state: DeepResearchState):
    prompt = research_planner_instruction.format(
        topic=state["topic"], max_sections=state["max_sections"]
    )
    result = llm.with_structured_output(ResearchPlannerOutput).invoke(prompt)
    return {"sections": result.sections}


def section_researcher(state: SectionResearchState):
    system_prompt = section_research_instruction.format(
        topic=state["research_topic"], section=state["section"]
    )
    llm_tools = llm.bind_tools([search_tool])
    messages = state.get("messages", None)
    if not messages:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Start research"),
        ]
        return {"messages": messages + [llm_tools.invoke(messages)]}
    return {"messages": [llm_tools.invoke(messages)]}


def extract_section_content(state: SectionResearchState):
    messages = state["messages"]
    last_message = messages[-1]
    return {"section_contents": [last_message.content]}


def conduct_section_researches(state: DeepResearchState):
    return [
        Send("section_research_graph", {"research_topic": state["topic"], "section": s})
        for s in state["sections"]
    ]


class ResearchWriterOutput(BaseModel):
    """Research Writer Output"""

    content: str = Field(description="The complete content of the research")


def research_writer(state: DeepResearchState):
    prompt = research_writer_intruction.format(
        topic=state["topic"], sections="\n\n".join(state["section_contents"])
    )
    output = llm.with_structured_output(ResearchWriterOutput).invoke(prompt)
    return {"final_report": output.content}
