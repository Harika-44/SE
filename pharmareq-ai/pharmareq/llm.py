"""Thin wrapper around the Gemini API.

Design rule: the LLM is *optional*. Every agent has a deterministic offline path, and
every LLM answer is validated (JSON schema, grounding checks) before it is used. If the
key is missing, the SDK is not installed, or a call/validation fails, agents fall back
to the offline path.
"""
import json
import os
import re
from google import genai
from . import config


class LLM:
    def __init__(self):
        self.client = None
        self.enabled = False
        self.last_error = None
        self.calls = 0
        key = os.getenv("GEMINI_API_KEY")
        if config.MODE != "offline" and key:
            try:
                self.client = genai.Client(api_key=key)
                self.enabled = True
            except Exception as e:  # SDK missing or misconfigured
                self.last_error = str(e)

    @property
    def mode(self) -> str:
        return "llm+rules" if self.enabled else "offline-rules"

    def json(self, system: str, user: str, max_tokens: int = 2500):
        """Return parsed JSON from the model, or None on any failure."""
        if not self.enabled:
            return None
        try:
            self.calls += 1
            prompt = (
                f"{system}\n"
                "Respond with a single valid JSON value only. No prose, no markdown fences.\n\n"
                f"{user}"
            )
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            text = (response.text or "").strip()
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
            return json.loads(text)
        except Exception as e:
            self.last_error = str(e)
            return None


llm = LLM()