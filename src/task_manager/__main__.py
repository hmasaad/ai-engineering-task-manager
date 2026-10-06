"""Run the task manager on this machine only."""

import argparse
import sys

import uvicorn

from task_manager.clock import SystemClock
from task_manager.web.app import create_app
from task_manager.workspace import Workspace

HOST = "127.0.0.1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Engineering Task Manager")
    parser.add_argument("--workspace", required=True, help="Path to the SQLite workspace file")
    parser.add_argument("--engineer", default="Engineer", help="Name copied onto verifications")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default=HOST)
    args = parser.parse_args(argv)
    if args.host != HOST:
        print("The server binds to 127.0.0.1 only.", file=sys.stderr)
        return 2
    workspace = Workspace(args.workspace, SystemClock(), args.engineer)
    uvicorn.run(create_app(workspace), host=HOST, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
