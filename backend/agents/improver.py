from config import section_headings
from llm import get_llm, load_prompt
from schemas.improver import ImproverOutput

PROMPT_TEMPLATE = load_prompt("improver")


def run_improver(topic: str, lesson_text: str, evaluation: dict) -> str:
    failed_checks = [k for k, v in evaluation["checks"].items() if not v]
    prompt = PROMPT_TEMPLATE.format(
        topic=topic,
        lesson=lesson_text,
        failed_checks=", ".join(failed_checks) if failed_checks else "none",
        reasons="\n".join(f"- {r}" for r in evaluation.get("reasons", [])) or "- (none)",
        section_headings="\n".join(f"## {h}" for h in section_headings(topic)),
    )
    llm = get_llm(temperature=0.0).with_structured_output(ImproverOutput, method="json_schema")
    result: ImproverOutput = llm.invoke(prompt)
    return result.updated_lesson
