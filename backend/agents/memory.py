"""Persistent memory: learns from repeated failures across executions.

Generic across topics on purpose - the failure->prompt-update mapping below
is about *kinds* of writing problems (missing example, too much jargon, ...),
never about a specific subject, so learning from a RAG run also helps later
lessons on unrelated topics.
"""

from config import MEMORY_FILE
from utils.logger import read_json, write_json

DEFAULT_MEMORY = {"common_failures": [], "prompt_updates": []}

# Maps a failed rubric check -> the durable prompt guidance it teaches the
# Generator for next time.
FAILURE_TO_GUIDANCE = {
    "length": "Keep the lesson within the target length - not too short, not too long.",
    "flow": "Keep every required section, in the exact required order.",
    "summary": "Always end with a real summary that recaps the key points.",
    "simple_language": "Keep sentences short. Use simple, everyday words.",
    "jargon_explained": "Always explain every technical term the moment it first appears.",
    "definition": "Always give a clear, simple definition of the topic early in the lesson.",
    "motivation": "Always clearly explain why the topic matters or is needed.",
    "workflow": "Always explain the step-by-step process of how the topic works.",
    "example": "Always include one realistic, concrete example a beginner can relate to.",
    "accuracy": "Double-check every fact stated in the lesson for correctness.",
}


def load_memory() -> dict:
    return read_json(MEMORY_FILE, dict(DEFAULT_MEMORY))


def save_memory(memory: dict) -> None:
    write_json(MEMORY_FILE, memory)


def update_memory(memory: dict, failed_checks: list[str]) -> dict:
    """Record failed checks and their prompt guidance, deduped, then persist."""
    common_failures = list(memory.get("common_failures", []))
    prompt_updates = list(memory.get("prompt_updates", []))

    for check in failed_checks:
        if check not in common_failures:
            common_failures.append(check)
        guidance = FAILURE_TO_GUIDANCE.get(check)
        if guidance and guidance not in prompt_updates:
            prompt_updates.append(guidance)

    memory = {"common_failures": common_failures, "prompt_updates": prompt_updates}
    save_memory(memory)
    return memory


def memory_guidance_block(memory: dict) -> str:
    updates = memory.get("prompt_updates", [])
    if not updates:
        return ""
    bullet_list = "\n".join(f"- {u}" for u in updates)
    return (
        "Guidance learned from previous lessons that failed evaluation "
        "(always apply these):\n" + bullet_list
    )
