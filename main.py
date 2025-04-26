from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from deep_research.agent import deep_research_graph

app = FastAPI()


class ResearchRequest(BaseModel):
    topic: str
    max_sections: int = 3


class ResearchResponse(BaseModel):
    final_report: str


@app.post("/api/research", response_model=ResearchResponse)
def research(request: ResearchRequest):
    state = deep_research_graph.invoke(
        {
            "topic": request.topic,
            "max_sections": request.max_sections,
        }
    )
    return ResearchResponse(final_report=state["final_report"])


@app.get("/", response_class=FileResponse)
async def web():
    return FileResponse(path="web/index.html", media_type="text/html")
