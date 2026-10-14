"""One workspace file. Pages and the HTTP API call these commands."""

import threading
from pathlib import Path

from task_manager.clock import ScriptedClock, SystemClock, format_time
from task_manager.domain import (
    branch,
    capture,
    commit_file,
    decisions,
    delete_file,
    dependency,
    file_read,
    folder,
    implementation,
    model_file,
    pull_request,
    requirement,
    status,
    subtasks,
    test_run,
    verification,
    workflow,
)
from task_manager.domain.results import Refusal
from task_manager.storage.connection import (
    call_in_transaction,
    connect,
    ensure_assistant,
    ensure_engineer,
)
from task_manager.storage.requirement_store import detail as requirement_detail
from task_manager.storage.requirement_store import list_payloads, trace_payloads
from task_manager.storage.task_store import list_top_level, task_detail


class Workspace:
    def __init__(
        self,
        path: str | Path,
        clock: SystemClock | ScriptedClock | None = None,
        engineer_name: str = "Engineer",
        assistant_name: str = "Assistant",
        project_root: str | Path | None = None,
        model=None,
    ) -> None:
        self.connection = connect(path)
        self.clock = clock or SystemClock()
        self._lock = threading.Lock()
        self.engineer_name = ensure_engineer(self.connection, engineer_name)
        self.assistant_name = ensure_assistant(self.connection, assistant_name)
        self.project_root = Path(project_root) if project_root is not None else Path.cwd()
        self.model = model

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

    def execution_order(self) -> list[dict[str, object]]:
        with self._lock:
            return dependency.execution_order(self.connection)

    def add_prerequisite(self, task_id: int, prerequisite_id: int | None):
        return self._run(
            lambda conn, _at: dependency.add(conn, task_id, prerequisite_id)
        )

    def remove_prerequisite(self, task_id: int, prerequisite_id: int):
        return self._run(
            lambda conn, _at: dependency.remove(conn, task_id, prerequisite_id)
        )

    def add_workflow_step(
        self,
        task_id: int,
        title: str | None,
        action: str | None,
        project: str | None,
        path: str | None,
        what_changed: str | None,
        change_class: str | None,
    ):
        return self._run(
            lambda conn, _at: workflow.add(
                conn,
                task_id,
                title,
                action,
                project,
                path,
                what_changed,
                change_class,
            )
        )

    def remove_workflow_step(self, task_id: int, step_id: int):
        return self._run(lambda conn, _at: workflow.remove(conn, task_id, step_id))

    def advance_workflow(self, task_id: int):
        root = self.project_root
        return self._run(lambda conn, at: workflow.advance(conn, task_id, at, root))

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
        method: str | None = None,
        run_identifier: str | None = None,
    ):
        return self._run(
            lambda conn, at: capture.verify(
                conn,
                task_id,
                criterion_id,
                observation,
                pass_result,
                method,
                run_identifier,
                at,
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

    def record_model_file(
        self,
        task_id: int,
        project: str | None,
        change_class: str | None,
        what_changed: str | None,
        stopped: bool = False,
        file_path: str | None = None,
        file_read_id: int | None = None,
    ):
        root = self.project_root
        model = self.model
        return self._run(
            lambda conn, at: model_file.record_model_file(
                conn,
                task_id,
                project,
                change_class,
                what_changed,
                stopped,
                file_path,
                file_read_id,
                at,
                root,
                model,
            )
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

    def record_folder(
        self,
        task_id: int,
        project: str | None,
        change_class: str | None,
        what_changed: str | None,
        stopped: bool,
        folder_path: str | None,
    ):
        root = self.project_root
        return self._run(
            lambda conn, at: folder.record(
                conn,
                task_id,
                project,
                change_class,
                what_changed,
                stopped,
                folder_path,
                at,
                root,
            )
        )

    def record_test(
        self,
        task_id: int,
        project: str | None,
        change_class: str | None,
        what_changed: str | None,
        stopped: bool,
        test_path: str | None,
    ):
        root = self.project_root
        return self._run(
            lambda conn, at: test_run.record(
                conn,
                task_id,
                project,
                change_class,
                what_changed,
                stopped,
                test_path,
                at,
                root,
            )
        )

    def record_deletion(
        self,
        task_id: int,
        project: str | None,
        change_class: str | None,
        what_changed: str | None,
        stopped: bool,
        file_path: str | None,
    ):
        root = self.project_root
        return self._run(
            lambda conn, at: delete_file.record(
                conn,
                task_id,
                project,
                change_class,
                what_changed,
                stopped,
                file_path,
                at,
                root,
            )
        )

    def record_branch(
        self,
        task_id: int,
        project: str | None,
        change_class: str | None,
        what_changed: str | None,
        stopped: bool,
        branch_name: str | None,
    ):
        root = self.project_root
        return self._run(
            lambda conn, at: branch.record(
                conn,
                task_id,
                project,
                change_class,
                what_changed,
                stopped,
                branch_name,
                at,
                root,
            )
        )

    def record_commit(
        self,
        task_id: int,
        project: str | None,
        change_class: str | None,
        what_changed: str | None,
        stopped: bool,
        file_path: str | None,
    ):
        root = self.project_root
        return self._run(
            lambda conn, at: commit_file.record(
                conn,
                task_id,
                project,
                change_class,
                what_changed,
                stopped,
                file_path,
                at,
                root,
            )
        )

    def record_pull_request(
        self,
        task_id: int,
        project: str | None,
        change_class: str | None,
        what_changed: str | None,
        stopped: bool,
        branch: str | None,
    ):
        root = self.project_root
        return self._run(
            lambda conn, at: pull_request.record(
                conn,
                task_id,
                project,
                change_class,
                what_changed,
                stopped,
                branch,
                at,
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

    def record_assistant_check(
        self,
        task_id: int,
        change_id: int,
        criterion_id: int | None,
        evidence: str | None,
        result: str | None,
    ):
        return self._run(
            lambda conn, at: verification.record_assistant(
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


    def list_requirements(self) -> list[dict[str, object]]:
        with self._lock:
            return list_payloads(self.connection)

    def traceability(self) -> dict[str, object]:
        with self._lock:
            return trace_payloads(self.connection)

    def get_requirement(self, requirement_id: int):
        with self._lock:
            detail = requirement_detail(self.connection, requirement_id)
        if detail is None:
            from task_manager.domain.results import missing

            return missing("Requirement not found.")
        return detail

    def record_requirement(self, statement: str | None, kind: str | None):
        return self._run(lambda conn, at: requirement.record(conn, statement, kind, at))

    def change_requirement(self, requirement_id: int, statement: str | None, kind: str | None):
        return self._run(
            lambda conn, at: requirement.change(conn, requirement_id, statement, kind, at)
        )

    def link_requirement_task(self, requirement_id: int, task_id: int | None):
        return self._run(lambda conn, _at: requirement.link_task(conn, requirement_id, task_id))

    def link_requirement_criterion(
        self,
        requirement_id: int,
        task_id: int | None,
        criterion_id: int | None,
    ):
        return self._run(
            lambda conn, _at: requirement.link_criterion(
                conn, requirement_id, task_id, criterion_id
            )
        )

    def unlink_requirement_task(self, requirement_id: int, task_id: int):
        return self._run(
            lambda conn, _at: requirement.unlink_task(conn, requirement_id, task_id)
        )

    def unlink_requirement_criterion(self, requirement_id: int, criterion_id: int):
        return self._run(
            lambda conn, _at: requirement.unlink_criterion(conn, requirement_id, criterion_id)
        )

    def name_requirement_check(self, requirement_id: int, name: str | None):
        return self._run(lambda conn, _at: requirement.name_check(conn, requirement_id, name))

    def remove_requirement_check(self, requirement_id: int, check_id: int):
        return self._run(
            lambda conn, at: requirement.remove_check(conn, requirement_id, check_id, at)
        )

    def record_requirement_run(
        self,
        requirement_id: int,
        check_name: str | None,
        result: str | None,
        run_identifier: str | None,
    ):
        return self._run(
            lambda conn, at: requirement.record_run(
                conn, requirement_id, check_name, result, run_identifier, at
            )
        )


def is_refusal(result: object) -> bool:
    return isinstance(result, Refusal)
