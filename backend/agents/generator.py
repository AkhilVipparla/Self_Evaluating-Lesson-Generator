from agents.memory import memory_guidance_block
from config import LEARNER_PROFILE, section_headings
from llm import get_llm, load_prompt
from schemas.lesson import LessonOutput

PROMPT_TEMPLATE = load_prompt("generator")


def run_generator(topic: str, planner_output: dict, memory: dict) -> LessonOutput:
    prompt = PROMPT_TEMPLATE.format(
        topic=topic,
        audience=planner_output.get("audience", LEARNER_PROFILE["audience"]),
        learning_goals="\n".join(f"- {g}" for g in planner_output.get("learning_goals", [])),
        avoid="\n".join(f"- {a}" for a in planner_output.get("avoid", [])),
        memory_guidance=memory_guidance_block(memory),
        section_headings="\n".join(f"## {h}" for h in section_headings(topic)),
    )
    llm = get_llm(temperature=0.6).with_structured_output(LessonOutput, method="json_schema")
    return llm.invoke(prompt)
