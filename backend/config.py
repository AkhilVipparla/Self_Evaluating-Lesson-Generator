import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

MAX_RETRIES = 2

MEMORY_DIR = BASE_DIR / "memory"
LOGS_DIR = BASE_DIR / "logs"
MEMORY_FILE = MEMORY_DIR / "memory.json"
HISTORY_FILE = MEMORY_DIR / "history.json"
ATTEMPTS_FILE = LOGS_DIR / "attempts.json"
REJECTIONS_FILE = LOGS_DIR / "rejections.json"

# Shown as a placeholder/example in the UI only - the system itself must work
# for any topic the user submits, not just this one.
EXAMPLE_TOPIC = "Introduction to Retrieval-Augmented Generation (RAG)"

# Fixed learner persona - constant across every topic (CLAUDE.md "target learner").
LEARNER_PROFILE = {
    "audience": "12th-grade graduate in India, non-English-medium background",
    "constraints": [
        "Limited English vocabulary - use short, simple sentences",
        "No prior knowledge of the subject or of AI/technical concepts",
        "Every technical term must be explained in plain language the first time it appears",
        "Avoid unexplained jargon, advanced mathematics, and research-paper style language",
    ],
}

# Generic 7-section lesson template from CLAUDE.md. "{topic}" is substituted
# with whatever topic the user submits - never hardcoded to a specific subject.
SECTION_TEMPLATE = [
    "Introduction",
    "What is {topic}",
    "Why {topic} is needed",
    "How {topic} works",
    "Real-world example",
    "Key takeaways",
    "Summary",
]


def section_headings(topic: str) -> list[str]:
    return [s.format(topic=topic) for s in SECTION_TEMPLATE]
