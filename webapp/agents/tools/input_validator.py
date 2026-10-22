"""
Input validation & sanitization (AWS Bedrock best practice: "Input Validation").

Per the AWS prompt-injection guidance, user input must be validated and
sanitized before it reaches the model/tokenizer: bound its length, strip control
characters, and neutralize common prompt-structure spoofing markers. This runs
BEFORE any LLM call as the first line of defense (defense-in-depth with the
local injection regex and Amazon Bedrock Guardrails).

Reference: https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-injection.html
"""
import re

# Hard cap on a single supplier message. Long payloads are a classic vector for
# burying injection instructions; procurement chat turns are short by nature.
MAX_INPUT_CHARS = 2000

# Control characters (except tab/newline/carriage-return) have no place in chat.
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Structural markers used to spoof chat/role boundaries or fake system turns.
# We DEFANG (annotate) rather than silently drop, so the audit trail stays honest
# and the downstream injection detector can still see the attempt.
_SPOOF_MARKERS = [
    (re.compile(r"(?i)\bsystem\s*:"), "system\u200b:"),
    (re.compile(r"(?i)\bassistant\s*:"), "assistant\u200b:"),
    (re.compile(r"(?i)</?(system|assistant|user)>"), "[tag]"),
    (re.compile(r"\[/?INST\]"), "[inst]"),
    (re.compile(r"(?i)<\|.*?\|>"), "[token]"),
]


def sanitize_user_input(text: str) -> dict:
    """
    Validate and sanitize a raw supplier message.

    Returns:
      {
        "clean": str,            # sanitized text safe to feed downstream
        "original_length": int,
        "truncated": bool,
        "modified": bool,        # True if any sanitization changed the text
        "notes": [str],          # human-readable list of actions taken
      }
    Never raises; always returns a usable (possibly empty) string.
    """
    notes = []
    if text is None:
        return {"clean": "", "original_length": 0, "truncated": False, "modified": False, "notes": []}

    original = str(text)
    original_length = len(original)
    clean = original

    # 1) Strip control characters.
    stripped = _CONTROL_CHARS.sub("", clean)
    if stripped != clean:
        notes.append("removed control characters")
        clean = stripped

    # 2) Enforce length bound.
    truncated = False
    if len(clean) > MAX_INPUT_CHARS:
        clean = clean[:MAX_INPUT_CHARS]
        truncated = True
        notes.append(f"truncated to {MAX_INPUT_CHARS} chars")

    # 3) Defang role/prompt-structure spoofing markers (zero-width break inserted).
    for pattern, replacement in _SPOOF_MARKERS:
        new_clean = pattern.sub(replacement, clean)
        if new_clean != clean:
            notes.append("neutralized prompt-structure marker")
            clean = new_clean

    # 4) Collapse excessive whitespace runs (another padding/obfuscation vector).
    collapsed = re.sub(r"[ \t]{4,}", "   ", clean)
    collapsed = re.sub(r"\n{4,}", "\n\n\n", collapsed)
    if collapsed != clean:
        notes.append("collapsed excessive whitespace")
        clean = collapsed

    clean = clean.strip()
    modified = clean != original or truncated

    return {
        "clean": clean,
        "original_length": original_length,
        "truncated": truncated,
        "modified": modified,
        "notes": notes,
    }
