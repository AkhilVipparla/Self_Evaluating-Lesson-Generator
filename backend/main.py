from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agents.memory import load_memory
from config import EXAMPLE_TOPIC, HISTORY_FILE
from graph import run_lesson_pipeline
from utils.logger import append_json_log, read_json

app = FastAPI(title="Self-Evaluating Lesson Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    topic: str = Field(min_length=1)


@app.get("/api/example-topic")
def example_topic():
    return {"example_topic": EXAMPLE_TOPIC}


@app.post("/api/generate")
def generate(req: GenerateRequest):
    topic = req.topic.strip()
    result = run_lesson_pipeline(topic)

    response = {
        "topic": topic,
        "final_lesson": result["final_output"],
        "evaluation": result["evaluation"],
        "retry_count": result["retry_count"],
        "rejection_log": result["rejection_log"],
        "memory_updates": result["memory"],
    }

    append_json_log(
        HISTORY_FILE,
        {
            "topic": topic,
            "passed": result["final_output"].get("passed", False),
            "retry_count": result["retry_count"],
        },
    )

    return response


@app.get("/api/memory")
def get_memory():
    return load_memory()


@app.get("/api/history")
def get_history():
    return read_json(HISTORY_FILE, [])
