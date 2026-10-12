"""Run the task manager on this machine only."""

import argparse
import sys

import uvicorn

from task_manager.clock import SystemClock
from task_manager.model import ScriptedModel
from task_manager.web.app import create_app
from task_manager.workspace import Workspace

HOST = "127.0.0.1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Engineering Task Manager")
    parser.add_argument("--workspace", required=True, help="Path to the SQLite workspace file")
    parser.add_argument("--engineer", default="Engineer", help="Name copied onto verifications")
    parser.add_argument("--assistant", default="Assistant", help="Name copied onto assistant changes")
    parser.add_argument("--model-name", default=None, help="Name of the configured model")
    parser.add_argument("--model-text", default=None, help="Text the configured model returns")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default=HOST)
    args = parser.parse_args(argv)
    if args.host != HOST:
        print("The server binds to 127.0.0.1 only.", file=sys.stderr)
        return 2
    model = None
    if args.model_name is not None or args.model_text is not None:
        if not args.model_name or args.model_text is None:
            print("Name the model and the text it returns.", file=sys.stderr)
            return 2
        model = ScriptedModel(args.model_name, args.model_text)
    workspace = Workspace(
        args.workspace, SystemClock(), args.engineer, args.assistant, model=model
    )
    uvicorn.run(create_app(workspace), host=HOST, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
