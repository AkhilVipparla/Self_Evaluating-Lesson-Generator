from pathlib import Path

from langchain_groq import ChatGroq

from config import GROQ_API_KEY, GROQ_MODEL

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def get_llm(temperature: float = 0.1) -> ChatGroq:
    return ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=temperature)


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")
