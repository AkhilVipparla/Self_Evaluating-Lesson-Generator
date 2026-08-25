import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def append_json_log(path: Path, entry: dict[str, Any]) -> None:
    entries = read_json(path, [])
    entry = {"timestamp": datetime.now(timezone.utc).isoformat(), **entry}
    entries.append(entry)
    write_json(path, entries)


def log_attempt(path: Path, *, topic: str, attempt: int, prompt_version: str, checks: dict, passed: bool) -> None:
    append_json_log(
        path,
        {
            "topic": topic,
            "attempt": attempt,
            "prompt_version": prompt_version,
            "checks": checks,
            "passed": passed,
        },
    )


def log_rejection(path: Path, *, topic: str, attempt: int, checks: dict, reasons: list[str]) -> None:
    append_json_log(
        path,
        {
            "topic": topic,
            "attempt": attempt,
            "checks": checks,
            "reasons": reasons,
        },
    )
