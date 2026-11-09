# AI Q&A Bot

A small multi-turn CLI chatbot built with Python and the IO Intelligence API. The API is OpenAI-compatible, so the project uses the official OpenAI SDK with a custom `base_url`.

## What it does

- Multi-turn conversation with in-memory history
- Streaming responses in the terminal
- Simple history trimming so context does not grow forever
- Retry handling for temporary API failures
- Friendly CLI commands: `/clear`, `/history`, `/help`, `/exit`

## Stack

- Python 3.10+
- OpenAI Python SDK
- IO Intelligence API
- python-dotenv
- Rich

## Setup

### Windows

```bat
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your IO Intelligence API key:

```text
IO_API_KEY=your_key_here
```

## Run

```bash
python main.py
```

Disable streaming:

```bash
python main.py --no-stream
```

## Test

```bash
pytest
```

The tests use a fake client, so they do not call the API or need an API key.

## Example

```text
you> explain the difference between RAG and fine-tuning
assistant> ...
```

## Limitations

- Conversation history only lives in memory; closing the process clears it.
- History is trimmed by message count, not by token count.
- This is a chatbot, not an autonomous agent: it does not call tools or execute actions.

## CV bullet

```text
Multi-turn LLM Chatbot — Python, IO Intelligence API, Nemotron 3.5 Lightning
Built a multi-turn CLI chatbot using an OpenAI-compatible API, with conversation memory, streaming responses, retry handling, and environment-based API key management.
```
