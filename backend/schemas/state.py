from typing import Any, TypedDict


class GraphState(TypedDict):
    topic: str
    planner_output: dict[str, Any]
    lesson: dict[str, Any]
    evaluation: dict[str, Any]
    retry_count: int
    rejection_log: list[dict[str, Any]]
    memory: dict[str, Any]
    final_output: dict[str, Any]
