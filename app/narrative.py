"""Optional narrative layer (Future AI Enhancement, §37).

Turns a structured artifact into a plain-English paragraph. Uses a LOCAL Ollama
model if one is running (free, offline); otherwise falls back to a deterministic
extractive summary. Either way it only ever produces *narrative* — it never
alters scores, confidence, or any deterministic output. Clearly labelled so the
"explainable core" guarantee holds even when an LLM is opted in.
"""
from __future__ import annotations
import json
import urllib.request

import config
from vault import load_vault

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.2"   # small local instruct model; change to taste


def ollama_available(timeout: float = 2.0) -> bool:
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
        with urllib.request.urlopen(req, timeout=timeout):
            return True
    except Exception:
        return False


def _ollama(prompt: str, timeout: float = 60.0) -> str | None:
    try:
        body = json.dumps({"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}).encode()
        req = urllib.request.Request(OLLAMA_URL, data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read()).get("response", "").strip()
    except Exception:
        return None


def _extractive(note) -> str:
    """Deterministic fallback: stitch the note's own key sentences."""
    lines = [l.strip() for l in note.body.splitlines()
             if l.strip() and not l.startswith(("#", "|", ">", "-", "*"))]
    lead = " ".join(lines[:3])
    conf = note.confidence_state or "n/a"
    return (f"[{note.type}] {note.title}. Confidence: {conf}; freshness: "
            f"{note.freshness or 'n/a'}. {lead[:400]}").strip()


def summarize_note(name: str) -> dict:
    note = next((n for n in load_vault() if n.filename.lower() == name.lower()), None)
    if not note:
        return {"error": f"note '{name}' not found"}
    if ollama_available():
        prompt = (f"Summarize this strategic note in 2-3 plain sentences for a founder. "
                  f"Do NOT invent facts; only use what's given. Note:\n\n{note.body[:2500]}")
        text = _ollama(prompt)
        if text:
            return {"note": note.filename, "engine": f"ollama:{OLLAMA_MODEL}",
                    "summary": text, "disclaimer": "Narrative only — does not alter any score or confidence."}
    return {"note": note.filename, "engine": "extractive (deterministic fallback)",
            "summary": _extractive(note),
            "disclaimer": "Narrative only — does not alter any score or confidence."}


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    name = sys.argv[1] if len(sys.argv) > 1 else "T-two-sided-incentives-drive-referral-virality"
    print(f"Ollama available: {ollama_available()}\n")
    r = summarize_note(name)
    print(f"[{r.get('engine')}]\n{r.get('summary', r.get('error'))}")
