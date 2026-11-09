from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv
from rich.console import Console

from chat import ChatSession, DEFAULT_MODEL

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Multi-turn CLI chatbot for IO Intelligence."
    )
    parser.add_argument(
        "--model",
        default=os.getenv("IO_MODEL", DEFAULT_MODEL),
        help="Model ID to use.",
    )
    parser.add_argument(
        "--max-history",
        type=int,
        default=20,
        help="Maximum number of chat messages kept in context.",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming output.",
    )
    return parser


def main() -> int:
    load_dotenv()
    args = build_parser().parse_args()

    if not os.getenv("IO_API_KEY"):
        console.print(
            "[red]IO_API_KEY is not set.[/] Copy .env.example to .env and add your key."
        )
        return 1

    session = ChatSession(
        model=args.model,
        max_history_messages=args.max_history,
    )

    console.print("[bold]IO Intelligence CLI chatbot[/]")
    console.print(f"model: [cyan]{session.model}[/]")
    console.print("commands: /clear, /history, /help, /exit")
    console.print()

    while True:
        try:
            user_message = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nbye.")
            return 0

        if not user_message:
            continue

        command = user_message.lower()
        if command in {"/exit", "/quit"}:
            console.print("bye.")
            return 0
        if command == "/clear":
            session.clear()
            console.print("[dim]history cleared.[/]")
            continue
        if command == "/history":
            for message in session.get_history():
                console.print(f"[dim]{message['role']}:[/] {message['content']}")
            continue
        if command == "/help":
            console.print("commands: /clear, /history, /help, /exit")
            continue

        try:
            if args.no_stream:
                answer = session.ask(user_message)
                console.print(f"[bold green]assistant>[/] {answer}")
            else:
                console.print("[bold green]assistant>[/] ", end="")
                for chunk in session.stream_reply(user_message):
                    console.print(chunk, end="", markup=False, highlight=False)
                console.print()
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]error:[/] {exc}")


if __name__ == "__main__":
    sys.exit(main())
