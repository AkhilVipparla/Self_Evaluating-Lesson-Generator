"""Deterministic, topic-agnostic rubric checks used by the Evaluation Agent.

None of these checks reference any specific subject - the required section
headings are derived from whatever `topic` string is passed in, and the
jargon heuristic works off a generic common-English wordlist rather than a
fixed list of domain terms.
"""

import re

from config import section_headings

MIN_WORDS = 300
MAX_WORDS = 1500
MAX_AVG_SENTENCE_WORDS = 24
MIN_UNCOMMON_WORD_LENGTH = 8

# A modest set of very common English words/function words. Anything longer
# than MIN_UNCOMMON_WORD_LENGTH and NOT in this set is treated as a candidate
# "technical term" that must be explained on first use.
COMMON_WORDS = {
    "about", "after", "again", "against", "almost", "already", "although",
    "always", "another", "answer", "anything", "around", "because", "become",
    "before", "beginning", "believe", "between", "different", "difficult",
    "during", "easier", "easily", "enough", "everyone", "everything",
    "example", "explain", "explains", "explained", "following", "however",
    "important", "including", "information", "interesting", "learning",
    "little", "necessary", "needed", "numbers", "outside", "particular",
    "possible", "practice", "problem", "problems", "provide", "provides",
    "question", "questions", "remember", "sentence", "sentences", "several",
    "similar", "something", "sometimes", "students", "suggest", "surprise",
    "teacher", "teaching", "themselves", "therefore", "thinking", "thought",
    "through", "together", "understand", "understanding", "using", "usually",
    "without", "working", "written", "yourself", "beginner", "beginners",
    "lesson", "summary", "introduction", "takeaway", "takeaways",
    "everyday", "answering", "automatically", "combine", "combines",
    "combined", "traditional", "accurate", "accurately", "reliable",
    "reducing", "reduces", "computer", "computers", "internet", "database",
    "document", "documents", "language", "solution", "solutions",
}

# Hyphen/dash look-alikes an LLM may use in headings (non-breaking hyphen, en
# dash, em dash, minus sign, ...) - normalized to a plain "-" before any
# heading match so typography differences don't cause false "missing
# section" failures.
_DASH_TRANSLATION = str.maketrans({c: "-" for c in "‐‑‒–—―−"})


def _normalize_dashes(text: str) -> str:
    return text.translate(_DASH_TRANSLATION)


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def check_length(lesson_text: str) -> tuple[bool, str | None]:
    count = word_count(lesson_text)
    if count < MIN_WORDS:
        return False, f"Lesson is too short ({count} words, minimum {MIN_WORDS})."
    if count > MAX_WORDS:
        return False, f"Lesson is too long ({count} words, maximum {MAX_WORDS})."
    return True, None


def _find_heading_positions(lesson_text: str, headings: list[str]) -> list[int]:
    positions = []
    for heading in headings:
        pattern = re.compile(
            r"^#{1,6}\s*" + re.escape(heading) + r"\s*$", re.IGNORECASE | re.MULTILINE
        )
        match = pattern.search(lesson_text)
        positions.append(match.start() if match else -1)
    return positions


def check_flow(lesson_text: str, topic: str) -> tuple[bool, str | None]:
    headings = [_normalize_dashes(h) for h in section_headings(topic)]
    normalized_text = _normalize_dashes(lesson_text)
    positions = _find_heading_positions(normalized_text, headings)
    missing = [h for h, p in zip(headings, positions) if p == -1]
    if missing:
        return False, f"Missing required section(s): {', '.join(missing)}."
    found_positions = [p for p in positions if p != -1]
    if found_positions != sorted(found_positions):
        return False, "Sections are present but out of order."
    return True, None


def check_summary(lesson_text: str, topic: str) -> tuple[bool, str | None]:
    headings = [_normalize_dashes(h) for h in section_headings(topic)]
    normalized_text = _normalize_dashes(lesson_text)
    summary_heading = headings[-1]
    pattern = re.compile(
        r"^#{1,6}\s*" + re.escape(summary_heading) + r"\s*$\n(.*)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(normalized_text)
    if not match:
        return False, "Lesson has no Summary section."
    body = match.group(1).strip()
    if word_count(body) < 15:
        return False, "Summary section is missing or too short to recap the lesson."
    return True, None


def check_simple_language(lesson_text: str) -> tuple[bool, str | None]:
    sentences = re.split(r"(?<=[.!?])\s+", lesson_text)
    sentences = [s for s in sentences if word_count(s) > 0]
    if not sentences:
        return False, "Could not find any sentences to evaluate."
    avg_len = sum(word_count(s) for s in sentences) / len(sentences)
    if avg_len > MAX_AVG_SENTENCE_WORDS:
        return False, (
            f"Sentences are too long on average ({avg_len:.1f} words); "
            "use shorter, simpler sentences."
        )
    return True, None


_EXPLANATION_CUES = re.compile(
    r"\b(means|means that|i\.e\.|that is|which means|in other words|refers to|"
    r"is a|is an|is the|are a|are an|known as|called|or simply)\b",
    re.IGNORECASE,
)


def check_jargon_explained(lesson_text: str) -> tuple[bool, str | None]:
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", lesson_text)
    candidates = {
        w for w in words
        if len(w) >= MIN_UNCOMMON_WORD_LENGTH and w.lower() not in COMMON_WORDS
    }
    if not candidates:
        return True, None

    sentences = re.split(r"(?<=[.!?])\s+", lesson_text)

    unexplained = []
    for term in candidates:
        pattern = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
        explained = False
        for i, sentence in enumerate(sentences):
            if not pattern.search(sentence):
                continue
            context = sentence if i + 1 >= len(sentences) else sentence + " " + sentences[i + 1]
            if "(" in sentence or _EXPLANATION_CUES.search(context):
                explained = True
                break
        if not explained:
            unexplained.append(term)

    # Allow a small amount of noise from the heuristic itself.
    if len(unexplained) > max(2, len(candidates) // 3):
        sample = ", ".join(sorted(set(unexplained))[:5])
        return False, f"Some technical terms are not explained when first used: {sample}."
    return True, None


def run_deterministic_checks(lesson_text: str, topic: str) -> tuple[dict[str, bool], list[str]]:
    checks: dict[str, bool] = {}
    reasons: list[str] = []

    for name, fn in (
        ("length", lambda: check_length(lesson_text)),
        ("flow", lambda: check_flow(lesson_text, topic)),
        ("summary", lambda: check_summary(lesson_text, topic)),
        ("simple_language", lambda: check_simple_language(lesson_text)),
        ("jargon_explained", lambda: check_jargon_explained(lesson_text)),
    ):
        passed, reason = fn()
        checks[name] = passed
        if not passed and reason:
            reasons.append(reason)

    return checks, reasons
