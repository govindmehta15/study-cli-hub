# quiz.py - CLI quiz/flashcard game.
#
# Flashcards are free and always available: write "Q: ... / A: ..." pairs
# anywhere in your notes and /quiz picks them up, no setup needed.
#
# AI-generated multiple-choice questions are bring-your-own-key (BYOK): each
# user supplies their own Anthropic API key via the ANTHROPIC_API_KEY env
# var. There is no shared secret anywhere in this public repo, and no cost
# to the maintainer - you pay only for your own usage, exactly like any
# other AI-powered CLI tool.
import json
import os

from study_cli_hub.paths import list_notes, subject_path

ANTHROPIC_API_KEY_ENV = "ANTHROPIC_API_KEY"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
FLASHCARD_EXTENSIONS = {"txt", "md"}


def is_ai_configured():
    return bool(os.environ.get(ANTHROPIC_API_KEY_ENV))


def extract_flashcards_from_text(text):
    """Parses 'Q: ...' / 'A: ...' pairs out of free-form note text."""
    lines = text.splitlines()
    cards = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line[:2].lower() == "q:":
            question = line[2:].strip()
            j = i + 1
            answer = None
            while j < len(lines):
                candidate = lines[j].strip()
                if candidate[:2].lower() == "a:":
                    answer = candidate[2:].strip()
                    break
                if candidate[:2].lower() == "q:":
                    break
                j += 1
            if question and answer:
                cards.append({"question": question, "answer": answer})
                i = j
        i += 1
    return cards


def collect_flashcards(user_folder, subject):
    """All Q:/A: flashcards found across a subject's text notes."""
    cards = []
    for filename in list_notes(user_folder, subject):
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in FLASHCARD_EXTENSIONS:
            continue
        path = os.path.join(subject_path(user_folder, subject), filename)
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except OSError:
            continue
        cards.extend(extract_flashcards_from_text(text))
    return cards


def collect_notes_text(user_folder, subject, max_chars=8000):
    """Concatenated plain-text note content for a subject, used as source
    material for AI question generation. Capped to keep prompts small."""
    chunks = []
    total = 0
    for filename in list_notes(user_folder, subject):
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in FLASHCARD_EXTENSIONS:
            continue
        path = os.path.join(subject_path(user_folder, subject), filename)
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except OSError:
            continue
        if not text.strip():
            continue
        chunks.append(f"--- {filename} ---\n{text}")
        total += len(text)
        if total >= max_chars:
            break
    return "\n\n".join(chunks)[:max_chars]


def generate_ai_questions(subject, notes_text, count=5):
    """BYOK multiple-choice question generation. Returns (questions, error);
    each question is {"question", "choices": [...], "answer_index"}."""
    api_key = os.environ.get(ANTHROPIC_API_KEY_ENV)
    if not api_key:
        return None, (
            "No ANTHROPIC_API_KEY set. Export your own Anthropic API key to "
            "use AI-generated questions - see the README's '/quiz' section."
        )

    try:
        import anthropic
    except ImportError:
        return None, (
            "The 'anthropic' package isn't installed. Run: "
            "pip install \"study-cli-hub[ai]\" (or: pip install anthropic)"
        )

    if not notes_text.strip():
        return None, f"No text notes found in '{subject}' to generate questions from."

    prompt = (
        f"Based on these study notes about \"{subject}\", write {count} multiple-choice "
        "quiz questions to help someone review the material.\n\n"
        f"Notes:\n{notes_text}\n\n"
        "Respond with ONLY a JSON array, no other text, in this exact shape:\n"
        '[{"question": "...", "choices": ["...", "...", "...", "..."], "answer_index": 0}]'
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=os.environ.get("STUDY_HUB_AI_MODEL", DEFAULT_MODEL),
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = "".join(block.text for block in resp.content if hasattr(block, "text")).strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:]
        questions = json.loads(raw)
        valid = [
            q for q in questions
            if isinstance(q, dict) and q.get("question") and q.get("choices")
            and isinstance(q.get("answer_index"), int)
        ]
        if not valid:
            return None, "AI response didn't contain any usable questions."
        return valid, None
    except json.JSONDecodeError:
        return None, "AI response wasn't valid JSON - try again."
    except Exception as e:
        return None, f"AI question generation failed: {e}"
