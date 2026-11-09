from __future__ import annotations

import os
import time
from typing import Iterator

from openai import OpenAI

DEFAULT_BASE_URL = "https://api.intelligence.io.solutions/api/v1"
DEFAULT_MODEL = "nvidia/nemotron-3.5-lightning"

SYSTEM_PROMPT = """You are a helpful, concise AI assistant.
Answer in the same language the user uses.
If you are unsure, say so instead of inventing details.
Keep answers practical and easy to scan."""


class ChatSession:
    """A small multi-turn chat wrapper around an OpenAI-compatible API."""

    def __init__(
        self,
        client=None,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        system_prompt: str = SYSTEM_PROMPT,
        max_history_messages: int = 20,
        temperature: float = 0.7,
    ) -> None:
        self.model = model or os.getenv("IO_MODEL", DEFAULT_MODEL)
        self.max_history_messages = max(2, max_history_messages)
        self.temperature = temperature
        self.system_prompt = system_prompt
        self._client = client or OpenAI(
            base_url=base_url or os.getenv("IO_BASE_URL", DEFAULT_BASE_URL),
            api_key=api_key or os.getenv("IO_API_KEY"),
        )
        self.history: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

    def clear(self) -> None:
        self.history = [{"role": "system", "content": self.system_prompt}]

    def get_history(self) -> list[dict[str, str]]:
        return [dict(message) for message in self.history]

    def _trim_history(self) -> None:
        limit = 1 + self.max_history_messages
        if len(self.history) <= limit:
            return

        system_message = self.history[0]
        tail = self.history[-self.max_history_messages :]
        if tail and tail[0]["role"] == "assistant":
            tail = tail[1:]
        self.history = [system_message, *tail]

    def _create(self, messages: list[dict[str, str]], stream: bool = False):
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                return self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    stream=stream,
                )
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt < 2:
                    time.sleep(1.5**attempt)
        raise RuntimeError(f"LLM request failed: {last_error}") from last_error

    def ask(self, user_message: str) -> str:
        if not user_message.strip():
            raise ValueError("Message cannot be empty.")

        self.history.append({"role": "user", "content": user_message})
        response = self._create(self.history)
        content = response.choices[0].message.content or ""
        self.history.append({"role": "assistant", "content": content})
        self._trim_history()
        return content

    def stream_reply(self, user_message: str) -> Iterator[str]:
        if not user_message.strip():
            raise ValueError("Message cannot be empty.")

        self.history.append({"role": "user", "content": user_message})
        stream = self._create(self.history, stream=True)
        parts: list[str] = []

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                parts.append(delta)
                yield delta

        content = "".join(parts)
        self.history.append({"role": "assistant", "content": content})
        self._trim_history()
