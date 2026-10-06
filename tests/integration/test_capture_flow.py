from datetime import datetime, timezone

from task_manager.clock import ScriptedClock
from task_manager.workspace import Workspace


def test_top_level_tasks_are_oldest_first_then_by_id(tmp_path):
    same_time = datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc)
    clock = ScriptedClock(times=[same_time, same_time, same_time])
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada")
    try:
        first = workspace.create_task("First")
        second = workspace.create_task("Second")
        workspace.set_goal(first["id"], "Ship the record")
        detail = workspace.add_criterion(first["id"], "The goal is visible")
        listed = workspace.list_tasks()
        assert [item["id"] for item in listed] == [first["id"], second["id"]]
        assert listed[0]["created_at"] == listed[1]["created_at"]
        assert detail["goal"] == "Ship the record"
        assert detail["criteria"][0]["state"] == "Unverified"
    finally:
        workspace.close()
