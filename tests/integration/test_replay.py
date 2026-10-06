from datetime import datetime, timezone

from task_manager.clock import ScriptedClock
from task_manager.workspace import Workspace


def _script(path, clock):
    workspace = Workspace(path, clock, "Ada")
    try:
        created = workspace.create_task("Add export")
        workspace.set_goal(created["id"], "Take the record")
        updated = workspace.add_criterion(created["id"], "The file contains the goal")
        ready = workspace.transition(updated["id"], "mark_ready")
        started = workspace.transition(ready["id"], "start")
        criterion_id = started["criteria"][0]["id"]
        verified = workspace.verify_criterion(
            started["id"], criterion_id, "The file included the goal.", "pass"
        )
        completed = workspace.transition(verified["id"], "complete")
        reopened = workspace.transition(completed["id"], "reopen", "A missed case was found")
        workspace.add_subtask(reopened["id"], "Write the checklist")
        detail = workspace.add_decision(
            reopened["id"],
            "Use one file",
            "One engineer has one workspace",
        )
        return _snapshot(workspace, detail["id"])
    finally:
        workspace.close()


def _snapshot(workspace, root_id):
    detail = workspace.get_task(root_id)
    return {
        "status": detail["status"],
        "criteria": [
            {"text": item["text"], "state": item["state"]} for item in detail["criteria"]
        ],
        "subtasks": [
            {"title": item["title"], "status": item["status"]} for item in detail["subtasks"]
        ],
        "decisions": [item["statement"] for item in detail["decisions"]],
        "history": [item["cause_code"] for item in detail["history"]],
        "order": [item["id"] for item in workspace.list_tasks()],
    }


def test_same_commands_and_clock_produce_the_same_outcome(tmp_path):
    start = datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc)
    first = _script(tmp_path / "one.db", ScriptedClock(start=start))
    second = _script(tmp_path / "two.db", ScriptedClock(start=start))
    assert first == second
    assert first["status"] == "In Progress"
    assert first["criteria"][0]["state"] == "Verified"
    assert first["subtasks"][0]["title"] == "Write the checklist"
