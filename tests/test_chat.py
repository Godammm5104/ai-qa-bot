from types import SimpleNamespace

import pytest

from chat import ChatSession


def message(content: str | None):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def chunk(content: str | None):
    return SimpleNamespace(
        choices=[SimpleNamespace(delta=SimpleNamespace(content=content))]
    )


class FakeCompletions:
    def __init__(self, responses):
        self.responses = list(responses)

    def create(self, **kwargs):
        return self.responses.pop(0)


class FakeClient:
    def __init__(self, responses):
        self.chat = SimpleNamespace(completions=FakeCompletions(responses))


def test_ask_returns_content_and_adds_history():
    session = ChatSession(client=FakeClient([message("hello there")]), model="test")

    assert session.ask("hi") == "hello there"
    assert session.history == [
        {"role": "system", "content": session.system_prompt},
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello there"},
    ]


def test_history_is_trimmed_but_system_prompt_is_kept():
    session = ChatSession(
        client=FakeClient([message("one"), message("two")]),
        model="test",
        max_history_messages=2,
    )

    session.ask("first")
    session.ask("second")

    assert session.history[0]["role"] == "system"
    assert session.history[0]["content"] == session.system_prompt
    assert [m["content"] for m in session.history[1:]] == ["second", "two"]


def test_stream_reply_yields_chunks_and_stores_full_answer():
    session = ChatSession(
        client=FakeClient([[chunk("hel"), chunk("lo")]]),
        model="test",
    )

    assert list(session.stream_reply("hi")) == ["hel", "lo"]
    assert session.history[-1] == {"role": "assistant", "content": "hello"}


def test_empty_message_is_rejected():
    session = ChatSession(client=FakeClient([]), model="test")

    with pytest.raises(ValueError, match="empty"):
        session.ask("   ")
