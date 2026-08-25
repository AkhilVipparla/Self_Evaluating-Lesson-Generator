from langgraph.graph import END, START, StateGraph

from agents.evaluator import run_evaluator
from agents.generator import run_generator
from agents.improver import run_improver
from agents.memory import load_memory, update_memory
from agents.planner import run_planner
from config import ATTEMPTS_FILE, MAX_RETRIES, REJECTIONS_FILE
from schemas.state import GraphState
from utils.logger import log_attempt, log_rejection


def planner_node(state: GraphState) -> dict:
    planner_output = run_planner(state["topic"])
    return {"planner_output": planner_output.model_dump()}


def generator_node(state: GraphState) -> dict:
    lesson = run_generator(state["topic"], state["planner_output"], state["memory"])
    return {"lesson": lesson.model_dump()}


def evaluator_node(state: GraphState) -> dict:
    evaluation = run_evaluator(state["topic"], state["lesson"]["lesson"])
    attempt = state["retry_count"] + 1

    log_attempt(
        ATTEMPTS_FILE,
        topic=state["topic"],
        attempt=attempt,
        prompt_version=f"v{attempt}",
        checks=evaluation["checks"],
        passed=evaluation["pass"],
    )

    rejection_log = list(state["rejection_log"])
    memory = state["memory"]

    if not evaluation["pass"]:
        log_rejection(
            REJECTIONS_FILE,
            topic=state["topic"],
            attempt=attempt,
            checks=evaluation["checks"],
            reasons=evaluation["reasons"],
        )
        rejection_log.append(
            {"attempt": attempt, "checks": evaluation["checks"], "reasons": evaluation["reasons"]}
        )
        failed_checks = [k for k, v in evaluation["checks"].items() if not v]
        memory = update_memory(memory, failed_checks)

    update: dict = {"evaluation": evaluation, "rejection_log": rejection_log, "memory": memory}

    if evaluation["pass"] or state["retry_count"] >= MAX_RETRIES:
        update["final_output"] = {
            "title": state["lesson"]["title"],
            "lesson": state["lesson"]["lesson"],
            "passed": evaluation["pass"],
        }

    return update


def improver_node(state: GraphState) -> dict:
    updated_lesson_text = run_improver(
        state["topic"], state["lesson"]["lesson"], state["evaluation"]
    )
    lesson = dict(state["lesson"])
    lesson["lesson"] = updated_lesson_text
    return {"lesson": lesson, "retry_count": state["retry_count"] + 1}


def route_after_evaluation(state: GraphState) -> str:
    if state["evaluation"]["pass"]:
        return "end"
    if state["retry_count"] < MAX_RETRIES:
        return "improve"
    return "end"


def build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("planner", planner_node)
    graph.add_node("generator", generator_node)
    graph.add_node("evaluator", evaluator_node)
    graph.add_node("improver", improver_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "generator")
    graph.add_edge("generator", "evaluator")
    graph.add_conditional_edges(
        "evaluator", route_after_evaluation, {"end": END, "improve": "improver"}
    )
    graph.add_edge("improver", "evaluator")

    return graph.compile()


def run_lesson_pipeline(topic: str) -> GraphState:
    app = build_graph()
    initial_state: GraphState = {
        "topic": topic,
        "planner_output": {},
        "lesson": {},
        "evaluation": {},
        "retry_count": 0,
        "rejection_log": [],
        "memory": load_memory(),
        "final_output": {},
    }
    return app.invoke(initial_state)
