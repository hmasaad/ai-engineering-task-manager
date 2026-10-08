"""Record, approve, and decline the change that carries out a task."""

import sqlite3
from pathlib import Path

from task_manager.domain.capture import CANCELLED, _detail
from task_manager.domain.results import bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import implementation_store, task_store
from task_manager.storage.connection import assistant_name, engineer_name

WHAT_CHANGED_REQUIRED = "An account of what changed is required."
CHOOSE_CLASS = "Choose ordinary or consequential."
MUST_BE_IN_PROGRESS = "The task must be In Progress."
START_FIRST = "Start the task first."
REOPEN_FIRST = "Reopen the task first."
EVIDENCE_REQUIRED = "An account of the evidence reviewed is required."
ORDINARY_NO_APPROVAL = "An ordinary change does not wait for approval."
ALREADY_CARRIED_OUT = "The change is already carried out."
CANNOT_BE_CARRIED_OUT = "It cannot be carried out."
APPROVAL_SAME_TASK = "The approval must name a change on that task."
CHANGE_NOT_FOUND = "Implementation change not found."
REASON_REQUIRED = "A reason is required."
CARRIED_OUT_STAYS = "A carried-out change stays in the record."
CHANGE_ON_TASK = "The change must be on that task."
NAME_PROJECT = "Name the project this change is for."
PROJECT_MUST_EXIST = "The project must already exist."
NAME_FILE = "Name the file this change writes."
FILE_OUTSIDE = "The file must stay inside the named project."
FOLDER_MUST_EXIST = "The folder for that file must already exist."
FILE_NOT_TEXT = "The file is not text."
FILE_MISMATCH = "The file no longer matches the text this change was proposed against."
ASSISTANT_CANNOT_APPROVE = "The assistant cannot approve a change."
ASSISTANT_CANNOT_DECLINE = "The assistant cannot decline a change."

_CLASSES = {"ordinary", "consequential"}


def record(
    connection: sqlite3.Connection,
    task_id: int,
    what_changed: str | None,
    change_class: str | None,
    occurred_at: str,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    text = clean(what_changed)
    if not text:
        return bad_request(WHAT_CHANGED_REQUIRED)
    if change_class not in _CLASSES:
        return bad_request(CHOOSE_CLASS)
    implementation_store.insert_change(
        connection,
        int(task["id"]),
        text,
        change_class,
        engineer_name(connection),
        occurred_at,
    )
    return _detail(connection, int(task["id"]))


def record_assistant(
    connection: sqlite3.Connection,
    task_id: int,
    project: str | None,
    change_class: str | None,
    what_changed: str | None,
    stopped: bool,
    occurred_at: str,
    file_path: str | None = None,
    file_text: str | None = None,
    project_root: Path | None = None,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    named_project = clean(project)
    if not named_project:
        return bad_request(NAME_PROJECT)
    root = project_root or Path.cwd()
    project_dir = _project_dir(named_project, root)
    if file_path is not None and not project_dir.is_dir():
        return bad_request(PROJECT_MUST_EXIST)
    text = clean(what_changed)
    if not text:
        return bad_request(WHAT_CHANGED_REQUIRED)
    if change_class not in _CLASSES:
        return bad_request(CHOOSE_CLASS)
    placed = None
    if file_path is not None:
        placed = _inspect_new_file(project_dir, file_path, file_text if file_text is not None else "")
        if not isinstance(placed, _Placement):
            return placed
    stored_class = change_class
    stopped_flag = 0
    if change_class == "ordinary" and stopped:
        stored_class = "consequential"
        stopped_flag = 1
    if placed is not None and (stored_class == "consequential" or placed.existed):
        stored_class = "consequential"
        if not (change_class == "ordinary" and stopped):
            stopped_flag = 0
    if placed is not None and stored_class == "ordinary":
        written = _create_exclusive(placed.target, placed.proposed)
        if written is None:
            stored_class = "consequential"
            placed = _read_existing(placed)
            if not isinstance(placed, _Placement):
                return placed
    change_id = implementation_store.insert_change(
        connection,
        int(task["id"]),
        text,
        stored_class,
        engineer_name(connection),
        occurred_at,
    )
    implementation_store.insert_assistant_change(
        connection,
        change_id,
        named_project,
        assistant_name(connection),
        stopped_flag,
    )
    if placed is not None:
        implementation_store.insert_applied_file(
            connection,
            change_id,
            placed.relative,
            0 if placed.existed else 1,
            placed.previous,
            placed.proposed,
        )
    return _detail(connection, int(task["id"]))


def approve(
    connection: sqlite3.Connection,
    task_id: int,
    change_id: int,
    evidence: str | None,
    occurred_at: str,
    actor: str | None = None,
    project_root: Path | None = None,
):
    if actor == "assistant":
        return conflict(ASSISTANT_CANNOT_APPROVE)
    located = _locate(connection, task_id, change_id, APPROVAL_SAME_TASK)
    if not isinstance(located, tuple):
        return located
    task, change = located
    if change["class"] == "ordinary":
        return conflict(ORDINARY_NO_APPROVAL)
    if change["kind"] == "approved":
        return conflict(ALREADY_CARRIED_OUT)
    if change["kind"] == "not_carried_out":
        return conflict(CANNOT_BE_CARRIED_OUT)
    if task["status"] != "In Progress":
        return conflict(MUST_BE_IN_PROGRESS)
    reviewed = clean(evidence)
    if not reviewed:
        return bad_request(EVIDENCE_REQUIRED)
    applied = implementation_store.row_applied_file(connection, int(change["id"]))
    if applied is not None:
        written = _write_approved(
            change["assistant_project"],
            applied,
            project_root or Path.cwd(),
        )
        if written is not None:
            return written
    implementation_store.insert_resolution(
        connection,
        int(change["id"]),
        "approved",
        reviewed,
        None,
        engineer_name(connection),
        occurred_at,
    )
    return _detail(connection, int(task["id"]))


def mark_not_carried_out(
    connection: sqlite3.Connection,
    task_id: int,
    change_id: int,
    reason: str | None,
    occurred_at: str,
    actor: str | None = None,
):
    if actor == "assistant":
        return conflict(ASSISTANT_CANNOT_DECLINE)
    located = _locate(connection, task_id, change_id, CHANGE_ON_TASK)
    if not isinstance(located, tuple):
        return located
    task, change = located
    if task["status"] != "In Progress":
        return conflict(MUST_BE_IN_PROGRESS)
    if change["class"] == "ordinary" or change["kind"] == "approved":
        return conflict(CARRIED_OUT_STAYS)
    if change["kind"] == "not_carried_out":
        return conflict(CANNOT_BE_CARRIED_OUT)
    kept = clean(reason)
    if not kept:
        return bad_request(REASON_REQUIRED)
    implementation_store.insert_resolution(
        connection,
        int(change["id"]),
        "not_carried_out",
        None,
        kept,
        engineer_name(connection),
        occurred_at,
    )
    return _detail(connection, int(task["id"]))


def awaiting_accounts(connection: sqlite3.Connection, task_id: int) -> list[str]:
    return [
        str(item["what_changed"])
        for item in implementation_store.changes_for(connection, task_id)
        if item["outcome"] == "Awaiting approval"
    ]


def _record_status(status: str):
    if status == "Draft":
        return conflict(MUST_BE_IN_PROGRESS)
    if status == "Ready":
        return conflict(START_FIRST)
    if status == "Completed":
        return conflict(REOPEN_FIRST)
    if status == "Cancelled":
        return conflict(CANCELLED)
    if status != "In Progress":
        return conflict(MUST_BE_IN_PROGRESS)
    return None


def _locate(connection: sqlite3.Connection, task_id: int, change_id: int, other_task_message: str):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    change = implementation_store.row_change(connection, change_id)
    if change is None:
        return missing(CHANGE_NOT_FOUND)
    if int(change["task_id"]) != int(task["id"]):
        return conflict(other_task_message)
    return task, change


class _Placement:
    def __init__(
        self,
        relative: str,
        target: Path,
        existed: bool,
        previous: str | None,
        proposed: str,
    ) -> None:
        self.relative = relative
        self.target = target
        self.existed = existed
        self.previous = previous
        self.proposed = proposed


def _project_dir(project: str, root: Path) -> Path:
    candidate = Path(project)
    if candidate.is_absolute():
        return candidate
    return Path(root) / candidate


def _relative_inside(file_path: str) -> str | None:
    raw = Path(file_path)
    if raw.is_absolute():
        return None
    current = Path()
    for part in raw.parts:
        if part in ("", "."):
            continue
        if part == "..":
            if current == Path():
                return None
            current = current.parent
            continue
        current = current / part
    if current == Path():
        return None
    return current.as_posix()


def _is_text(data: bytes) -> bool:
    if b"\x00" in data:
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
    except (OSError, ValueError):
        return False
    return True


def _inspect_new_file(project_dir: Path, file_path: str | None, proposed: str):
    named = clean(file_path)
    if not named:
        return bad_request(NAME_FILE)
    relative = _relative_inside(named)
    if relative is None:
        return conflict(FILE_OUTSIDE)
    project_resolved = project_dir.resolve()
    target = project_dir / relative
    parent = target.parent
    if not parent.is_dir():
        return bad_request(FOLDER_MUST_EXIST)
    if not _inside(parent, project_resolved):
        return conflict(FILE_OUTSIDE)
    if target.is_symlink() or target.exists():
        try:
            resolved = target.resolve(strict=True)
        except OSError:
            return conflict(FILE_OUTSIDE)
        if not _inside(resolved, project_resolved):
            return conflict(FILE_OUTSIDE)
        if target.is_dir():
            return bad_request(FILE_NOT_TEXT)
        data = target.read_bytes()
        if not _is_text(data):
            return bad_request(FILE_NOT_TEXT)
        return _Placement(relative, target, True, data.decode("utf-8"), proposed)
    return _Placement(relative, target, False, None, proposed)


def _create_exclusive(target: Path, text: str) -> bool:
    try:
        with target.open("x", encoding="utf-8", newline="") as handle:
            handle.write(text)
    except FileExistsError:
        return False
    return True


def _read_existing(placed: _Placement):
    data = placed.target.read_bytes()
    if not _is_text(data):
        return bad_request(FILE_NOT_TEXT)
    return _Placement(
        placed.relative,
        placed.target,
        True,
        data.decode("utf-8"),
        placed.proposed,
    )


def _write_approved(project: str | None, applied: sqlite3.Row, root: Path):
    if project is None:
        return conflict(FILE_OUTSIDE)
    project_dir = _project_dir(str(project), root)
    if not project_dir.is_dir():
        return conflict(FILE_OUTSIDE)
    relative = _relative_inside(str(applied["file_path"]))
    if relative is None:
        return conflict(FILE_OUTSIDE)
    project_resolved = project_dir.resolve()
    target = project_dir / relative
    parent = target.parent
    if not parent.is_dir() or not _inside(parent, project_resolved):
        return conflict(FILE_OUTSIDE)
    proposed = str(applied["file_text"])
    was_new = int(applied["was_new"]) == 1
    if was_new:
        if target.is_symlink() or target.exists():
            try:
                resolved = target.resolve(strict=True)
            except OSError:
                return conflict(FILE_OUTSIDE)
            if not _inside(resolved, project_resolved):
                return conflict(FILE_OUTSIDE)
            return conflict(FILE_MISMATCH)
        if not _create_exclusive(target, proposed):
            return conflict(FILE_MISMATCH)
        return None
    if target.is_symlink() or target.exists():
        try:
            resolved = target.resolve(strict=True)
        except OSError:
            return conflict(FILE_OUTSIDE)
        if not _inside(resolved, project_resolved):
            return conflict(FILE_OUTSIDE)
    if not target.is_file():
        return conflict(FILE_MISMATCH)
    data = target.read_bytes()
    if not _is_text(data) or data.decode("utf-8") != applied["previous_text"]:
        return conflict(FILE_MISMATCH)
    target.write_bytes(proposed.encode("utf-8"))
    return None
