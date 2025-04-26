from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from deep_research.utils.state import DeepResearchState, SectionResearchState
from deep_research.utils.tools import search_tool
from deep_research.utils.nodes import (
    conduct_section_researches,
    extract_section_content,
    research_planner,
    research_writer,
    section_researcher,
)


def section_research_should_tools(state: SectionResearchState):
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "extract_section_content"


# Section Research SubGraph
section_research_builder = StateGraph(SectionResearchState)
section_research_builder.add_node("section_researcher", section_researcher)
section_research_builder.add_node("tools", ToolNode([search_tool]))
section_research_builder.add_node("extract_section_content", extract_section_content)
section_research_builder.add_edge(START, "section_researcher")
section_research_builder.add_conditional_edges(
    "section_researcher",
    section_research_should_tools,
    ["tools", "extract_section_content"],
)
section_research_builder.add_edge("tools", "section_researcher")
section_research_builder.add_edge("extract_section_content", END)


# Deep Research Graph
deep_research_builder = StateGraph(DeepResearchState)
deep_research_builder.add_node("research_planner", research_planner)
deep_research_builder.add_node(
    "section_research_graph", section_research_builder.compile()
)
deep_research_builder.add_node("research_writer", research_writer)
deep_research_builder.add_edge(START, "research_planner")
deep_research_builder.add_conditional_edges(
    "research_planner", conduct_section_researches, ["section_research_graph"]
)
deep_research_builder.add_edge("section_research_graph", "research_writer")
deep_research_builder.add_edge("research_writer", END)

deep_research_graph = deep_research_builder.compile()
