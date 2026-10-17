
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent.assistant import run_agent

app = FastAPI(
    title="AI Student Mentor API",
    description="API for the AI Student Ecosystem",
    version="1.0.0"
)

# Development setting. Restrict origins before production deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    student: dict[str, Any]
    history: list[dict[str, str]] = Field(default_factory=list)


from agent.roadmap import generate_roadmap, answer_project_doubt, get_student_tech_hub_roadmap

class RoadmapRequest(BaseModel):
    project_name: str
    student: dict[str, Any] = Field(default_factory=dict)
    history: list[dict[str, str]] = Field(default_factory=list)

class DoubtRequest(BaseModel):
    question: str
    project_name: str
    student: dict[str, Any] = Field(default_factory=dict)
    history: list[dict[str, str]] = Field(default_factory=list)


@app.get("/")
def home():
    return {"message": "AI Student Mentor API is running!"}


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        return run_agent(
            message=request.message,
            student=request.student,
            history=request.history
        )
    except Exception as error:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(error).__name__}: {error}"
        )


@app.post("/roadmap")
def roadmap(request: RoadmapRequest):
    try:
        return generate_roadmap(
            project_name=request.project_name,
            student=request.student,
            history=request.history
        )
    except Exception as error:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(error).__name__}: {error}"
        )


@app.post("/doubt")
def doubt(request: DoubtRequest):
    try:
        ans = answer_project_doubt(
            question=request.question,
            project_name=request.project_name,
            student=request.student,
            history=request.history
        )
        return {"response": ans, "project": request.project_name}
    except Exception as error:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(error).__name__}: {error}"
        )


@app.get("/hub-roadmap/{project_name}")
def hub_roadmap(project_name: str):
    try:
        return get_student_tech_hub_roadmap(project_name)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"{type(error).__name__}: {error}"
        )



