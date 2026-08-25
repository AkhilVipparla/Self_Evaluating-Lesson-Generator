from llm import get_llm, load_prompt
from schemas.evaluation import SemanticChecks
from utils.helpers import run_deterministic_checks

PROMPT_TEMPLATE = load_prompt("evaluator")


def run_evaluator(topic: str, lesson_text: str) -> dict:
    det_checks, det_reasons = run_deterministic_checks(lesson_text, topic)

    prompt = PROMPT_TEMPLATE.format(topic=topic, lesson=lesson_text)
    llm = get_llm(temperature=0.0).with_structured_output(SemanticChecks, method="json_schema")
    semantic: SemanticChecks = llm.invoke(prompt)

    checks = {
        "definition": semantic.definition,
        "motivation": semantic.motivation,
        "workflow": semantic.workflow,
        "example": semantic.example,
        "accuracy": semantic.accuracy,
        **det_checks,
    }
    reasons = list(semantic.reasons) + det_reasons

    return {"pass": all(checks.values()), "checks": checks, "reasons": reasons}
