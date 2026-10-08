"""One workspace file. Pages and the HTTP API call these commands."""

import threading
from pathlib import Path

from task_manager.clock import ScriptedClock, SystemClock, format_time
from task_manager.domain import capture, decisions, file_read, implementation, status, subtasks, verification
from task_manager.domain.results import Refusal
from task_manager.storage.connection import (
    call_in_transaction,
    connect,
    ensure_assistant,
    ensure_engineer,
)
from task_manager.storage.task_store import list_top_level, task_detail


class Workspace:
    def __init__(
        self,
        path: str | Path,
        clock: SystemClock | ScriptedClock | None = None,
        engineer_name: str = "Engineer",
        assistant_name: str = "Assistant",
        project_root: str | Path | None = None,
    ) -> None:
        self.connection = connect(path)
        self.clock = clock or SystemClock()
        self._lock = threading.Lock()
        self.engineer_name = ensure_engineer(self.connection, engineer_name)
        self.assistant_name = ensure_assistant(self.connection, assistant_name)
        self.project_root = Path(project_root) if project_root is not None else Path.cwd()

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

    def record_change(
        self,
        task_id: int,
        what_changed: str | None,
        change_class: str | None,
        project: str | None = None,
        assistant_name: str | None = None,
    ):
        del project, assistant_name
        return self._run(
            lambda conn, at: implementation.record(
                conn, task_id, what_changed, change_class, at
            )
        )

    def record_file_read(
        self,
        task_id: int,
        project: str | None,
        file_path: str | None,
        assistant_name: str | None = None,
    ):
        del assistant_name
        root = self.project_root
        return self._run(
            lambda conn, at: file_read.read_file(conn, task_id, project, file_path, at, root)
        )

    def record_assistant_change(
        self,
        task_id: int,
        project: str | None,
        change_class: str | None,
        what_changed: str | None,
        stopped: bool = False,
        file_path: str | None = None,
        file_text: str | None = None,
    ):
        root = self.project_root
        return self._run(
            lambda conn, at: implementation.record_assistant(
                conn,
                task_id,
                project,
                change_class,
                what_changed,
                stopped,
                at,
                file_path,
                file_text,
                root,
            )
        )

    def approve_change(
        self,
        task_id: int,
        change_id: int,
        evidence: str | None,
        actor: str | None = None,
    ):
        root = self.project_root
        return self._run(
            lambda conn, at: implementation.approve(
                conn, task_id, change_id, evidence, at, actor, root
            )
        )

    def mark_change_not_carried_out(
        self,
        task_id: int,
        change_id: int,
        reason: str | None,
        actor: str | None = None,
    ):
        return self._run(
            lambda conn, at: implementation.mark_not_carried_out(
                conn, task_id, change_id, reason, at, actor
            )
        )

    def record_check(
        self,
        task_id: int,
        change_id: int,
        criterion_id: int | None,
        evidence: str | None,
        result: str | None,
    ):
        return self._run(
            lambda conn, at: verification.record(
                conn, task_id, change_id, criterion_id, evidence, result, at
            )
        )

    def add_decision(
        self,
        task_id: int,
        statement: str,
        rationale: str,
        supersedes: list[int] | None = None,
        check_id: int | None = None,
    ):
        del check_id
        return self._run(
            lambda conn, at: decisions.add_decision(
                conn, task_id, statement, rationale, supersedes, at
            )
        )

    def add_linked_decision(
        self,
        task_id: int,
        statement: str,
        rationale: str,
        check_id: int | None,
        supersedes: list[int] | None = None,
    ):
        return self._run(
            lambda conn, at: decisions.add_linked_decision(
                conn, task_id, statement, rationale, check_id, supersedes, at
            )
        )


def is_refusal(result: object) -> bool:
    return isinstance(result, Refusal)
