from operator import add
from typing import Annotated, List

from langgraph.graph import MessagesState
from typing_extensions import TypedDict


class DeepResearchState(TypedDict):
  topic: str
  max_sections: int
  sections: List[str]
  section_contents: Annotated[List[str], add]
  final_report: str


class SectionResearchState(MessagesState):
  research_topic: str
  section: str
  section_contents: List[str]