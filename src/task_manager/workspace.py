"""One workspace file. Pages and the HTTP API call these commands."""

import threading
from pathlib import Path

from task_manager.clock import ScriptedClock, SystemClock, format_time
from task_manager.domain import capture, decisions, status, subtasks
from task_manager.domain.results import Refusal
from task_manager.storage.connection import call_in_transaction, connect, ensure_engineer
from task_manager.storage.task_store import list_top_level, task_detail


class Workspace:
    def __init__(
        self,
        path: str | Path,
        clock: SystemClock | ScriptedClock | None = None,
        engineer_name: str = "Engineer",
    ) -> None:
        self.connection = connect(path)
        self.clock = clock or SystemClock()
        self._lock = threading.Lock()
        self.engineer_name = ensure_engineer(self.connection, engineer_name)

    def close(self) -> None:
        self.connection.close()

    def _run(self, operation):
        with self._lock:
            occurred_at = format_time(self.clock.now())
            return call_in_transaction(
                self.connection,
                lambda conn: operation(conn, occurred_at),
            )

    def list_tasks(self) -> list[dict[str, object]]:
        with self._lock:
            return list_top_level(self.connection)

    def get_task(self, task_id: int):
        with self._lock:
            detail = task_detail(self.connection, task_id)
        if detail is None:
            from task_manager.domain.results import missing

            return missing("Task not found.")
        return detail

    def create_task(self, title: str):
        return self._run(lambda conn, at: capture.create_task(conn, title, at))

    def set_goal(self, task_id: int, goal: str | None):
        return self._run(lambda conn, at: capture.set_goal(conn, task_id, goal, at))

    def add_criterion(self, task_id: int, text: str):
        return self._run(lambda conn, at: capture.add_criterion(conn, task_id, text))

    def update_criterion(self, task_id: int, criterion_id: int, text: str):
        return self._run(
            lambda conn, at: capture.update_criterion(conn, task_id, criterion_id, text, at)
        )

    def remove_criterion(self, task_id: int, criterion_id: int):
        return self._run(
            lambda conn, at: capture.remove_criterion(conn, task_id, criterion_id, at)
        )

    def transition(self, task_id: int, action: str, reason: str | None = None):
        return self._run(
            lambda conn, at: status.transition(conn, task_id, action, reason, at)
        )

    def verify_criterion(
        self,
        task_id: int,
        criterion_id: int,
        observation: str,
        pass_result: str,
    ):
        return self._run(
            lambda conn, at: capture.verify(
                conn, task_id, criterion_id, observation, pass_result, at
            )
        )

    def unverify_criterion(self, task_id: int, criterion_id: int):
        return self._run(lambda conn, at: capture.unverify(conn, task_id, criterion_id))

    def add_subtask(self, parent_id: int, title: str):
        return self._run(lambda conn, at: subtasks.add_subtask(conn, parent_id, title, at))

    def attach(self, child_id: int, parent_id: int):
        return self._run(lambda conn, _at: subtasks.attach(conn, child_id, parent_id))

    def add_decision(
        self,
        task_id: int,
        statement: str,
        rationale: str,
        supersedes: list[int] | None = None,
    ):
        return self._run(
            lambda conn, at: decisions.add_decision(
                conn, task_id, statement, rationale, supersedes, at
            )
        )


def is_refusal(result: object) -> bool:
    return isinstance(result, Refusal)
