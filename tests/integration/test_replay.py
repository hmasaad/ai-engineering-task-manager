from datetime import datetime, timezone

from task_manager.clock import ScriptedClock
from task_manager.workspace import Workspace


def _script(path, clock):
    workspace = Workspace(path, clock, "Ada", "Guide")
    try:
        created = workspace.create_task("Add export")
        workspace.set_goal(created["id"], "Take the record")
        updated = workspace.add_criterion(created["id"], "The file contains the goal")
        updated = workspace.add_criterion(updated["id"], "The export lists the date")
        ready = workspace.transition(updated["id"], "mark_ready")
        started = workspace.transition(ready["id"], "start")
        ordinary = workspace.record_change(started["id"], "Rename the export label", "ordinary")
        ordinary_id = ordinary["implementation_changes"][0]["id"]
        first_criterion = started["criteria"][0]["id"]
        second_criterion = started["criteria"][1]["id"]
        failed = workspace.record_check(
            started["id"], ordinary_id, first_criterion, "The label was still old", "Failed"
        )
        failed_check_id = failed["implementation_changes"][0]["checks"][0]["id"]
        workspace.add_linked_decision(
            started["id"],
            "Keep the earlier evidence",
            "The first check failed",
            failed_check_id,
        )
        workspace.record_check(
            started["id"], ordinary_id, first_criterion, "The label now reads Export", "Passed"
        )
        workspace.record_check(
            started["id"], ordinary_id, second_criterion, "The date is on the page", "Passed"
        )
        consequential = workspace.record_change(
            started["id"], "Replace the stored export name", "consequential"
        )
        change_id = consequential["implementation_changes"][1]["id"]
        workspace.approve_change(
            started["id"], change_id, "The detail page shows the new export name"
        )
        workspace.record_check(
            started["id"], change_id, first_criterion, "The new name is on the page", "Passed"
        )
        second = workspace.record_change(started["id"], "Drop the old export path", "consequential")
        second_id = second["implementation_changes"][2]["id"]
        workspace.mark_change_not_carried_out(
            started["id"], second_id, "The old path is still required"
        )
        verified = started
        for criterion in started["criteria"]:
            verified = workspace.verify_criterion(
                verified["id"], criterion["id"], "The file included the goal.", "pass"
            )
        completed = workspace.transition(verified["id"], "complete")
        reopened = workspace.transition(completed["id"], "reopen", "A missed case was found")
        workspace.add_subtask(reopened["id"], "Write the checklist")
        detail = workspace.add_decision(
            reopened["id"],
            "Use one file",
            "One engineer has one workspace",
        )
        workspace.record_assistant_change(
            reopened["id"], "billing", "ordinary", "Rename the export label", False
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
        "decisions": [
            {
                "statement": item["statement"],
                "check_id": None if item["check"] is None else item["check"]["id"],
                "evidence": None if item["check"] is None else item["check"]["evidence"],
                "result": None if item["check"] is None else item["check"]["result"],
            }
            for item in detail["decisions"]
        ],
        "history": [item["cause_code"] for item in detail["history"]],
        "changes": [
            {
                "what_changed": item["what_changed"],
                "class": item["class"],
                "outcome": item["outcome"],
                "project": item["project"],
                "assistant_name": item["assistant_name"],
                "recorded_by": item["recorded_by"],
                "checks": [check["result"] for check in item["checks"]],
            }
            for item in detail["implementation_changes"]
        ],
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
    assert first["decisions"][0]["statement"] == "Keep the earlier evidence"
    assert first["decisions"][0]["evidence"] == "The label was still old"
    assert first["decisions"][0]["result"] == "Failed"
    assert first["decisions"][0]["check_id"] == second["decisions"][0]["check_id"]
    assisted = next(item for item in first["changes"] if item["recorded_by"] == "assistant")
    assert assisted["what_changed"] == "Rename the export label"
    assert assisted["project"] == "billing"
    assert assisted["assistant_name"] == "Guide"
    assert assisted["class"] == "ordinary"
    assert assisted["outcome"] == "Carried out"
