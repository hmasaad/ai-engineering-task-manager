from datetime import datetime, timedelta, timezone

from task_manager.clock import ScriptedClock
from task_manager.domain.results import Refusal
from task_manager.workspace import Workspace


def test_decision_requires_statement_and_rationale(workspace):
    created = workspace.create_task("Add export")
    refused = workspace.add_decision(created["id"], "Use one file", "   ")
    assert isinstance(refused, Refusal)
    assert refused.code == 400
    assert workspace.get_task(created["id"])["decisions"] == []


def test_decision_can_supersede_several_earlier_decisions(workspace):
    created = workspace.create_task("Add export")
    first = workspace.add_decision(created["id"], "Use JSON", "Easy to read")
    second = workspace.add_decision(created["id"], "Use one table", "Fewer joins")
    third = workspace.add_decision(
        created["id"],
        "Use SQLite",
        "One file for one engineer",
        [first["decisions"][0]["id"], second["decisions"][1]["id"]],
    )
    decisions = third["decisions"]
    assert len(decisions) == 3
    assert decisions[2]["supersedes"] == [
        first["decisions"][0]["id"],
        second["decisions"][1]["id"],
    ]
    assert decisions[0]["statement"] == "Use JSON"
    assert decisions[1]["statement"] == "Use one table"


def test_cannot_supersede_another_tasks_decision_or_a_later_one(tmp_path):
    start = datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc)
    clock = ScriptedClock(
        times=[
            start,
            start + timedelta(hours=2),
            start + timedelta(hours=1),
            start,
        ]
    )
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada")
    try:
        first_task = workspace.create_task("First")
        other = workspace.create_task("Other")
        # clock: create uses start, second create uses start+2h, so the next decision is earlier
        own = workspace.add_decision(first_task["id"], "Own choice", "Because it fits")
        theirs = workspace.add_decision(other["id"], "Their choice", "Different task")
        # own was recorded at start+2h, this decision is recorded at start+1h, so own is later
        later = workspace.add_decision(
            first_task["id"],
            "Too early",
            "Clock went backwards",
            [own["decisions"][0]["id"]],
        )
        assert isinstance(later, Refusal)
        assert "after" in later.message.lower()
        cross = workspace.add_decision(
            first_task["id"],
            "Cross task",
            "Should fail",
            [theirs["decisions"][0]["id"]],
        )
        assert isinstance(cross, Refusal)
        assert "same task" in cross.message.lower()
        assert len(workspace.get_task(first_task["id"])["decisions"]) == 1
    finally:
        workspace.close()


def test_cancelled_task_refuses_a_decision(workspace):
    created = workspace.create_task("Add export")
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "Visible")
    ready = workspace.transition(created["id"], "mark_ready")
    started = workspace.transition(ready["id"], "start")
    cancelled = workspace.transition(started["id"], "cancel", "Stop")
    refused = workspace.add_decision(cancelled["id"], "A choice", "A reason")
    assert isinstance(refused, Refusal)
    assert "cancelled" in refused.message.lower()
