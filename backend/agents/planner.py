from config import LEARNER_PROFILE
from llm import get_llm, load_prompt
from schemas.planner import PlannerOutput

PROMPT_TEMPLATE = load_prompt("planner")


def run_planner(topic: str) -> PlannerOutput:
    prompt = PROMPT_TEMPLATE.format(
        topic=topic,
        audience=LEARNER_PROFILE["audience"],
        constraints="\n".join(f"- {c}" for c in LEARNER_PROFILE["constraints"]),
    )
    llm = get_llm(temperature=0.3).with_structured_output(PlannerOutput, method="json_schema")
    return llm.invoke(prompt)
