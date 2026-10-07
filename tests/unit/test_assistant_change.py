from task_manager.domain.results import Refusal
from task_manager.workspace import Workspace


def _started(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The file contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def test_ordinary_assistant_change_stores_the_account(tmp_path, clock):
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide")
    try:
        started = _started(workspace)
        recorded = workspace.record_assistant_change(
            started["id"], "  billing  ", "ordinary", "  Rename the export label  ", False
        )
        change = recorded["implementation_changes"][0]
        assert recorded["status"] == "In Progress"
        assert change["what_changed"] == "Rename the export label"
        assert change["class"] == "ordinary"
        assert change["outcome"] == "Carried out"
        assert change["project"] == "billing"
        assert change["assistant_name"] == "Guide"
        assert change["engineer_name"] == "Ada"
        assert change["recorded_by"] == "assistant"
        assert change["stopped"] is False
        assert change["approval"] is None
        assert change["checks"] == []
        assert recorded["criteria"][0]["state"] == "Unverified"
        assert recorded["decisions"] == started["decisions"]
        assert recorded["history"] == started["history"]
        assert not (tmp_path / "billing").exists()
    finally:
        workspace.close()


def test_status_is_checked_before_project_account_and_class(workspace):
    started = _started(workspace)
    workspace.connection.execute(
        "UPDATE task SET status = 'Draft' WHERE id = ?", (started["id"],)
    )
    refused = workspace.record_assistant_change(started["id"], "   ", None, "   ", False)
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."

    workspace.connection.execute(
        "UPDATE task SET status = 'Ready' WHERE id = ?", (started["id"],)
    )
    ready = workspace.record_assistant_change(
        started["id"], "billing", "ordinary", "Rename the export label", False
    )
    assert isinstance(ready, Refusal)
    assert ready.message == "Start the task first."

    workspace.connection.execute(
        "UPDATE task SET status = 'Completed' WHERE id = ?", (started["id"],)
    )
    completed = workspace.record_assistant_change(started["id"], "", "ordinary", "", False)
    assert isinstance(completed, Refusal)
    assert completed.message == "Reopen the task first."

    workspace.connection.execute(
        "UPDATE task SET status = 'In Progress' WHERE id = ?", (started["id"],)
    )
    blank_project = workspace.record_assistant_change(
        started["id"], "   ", "ordinary", "   ", False
    )
    assert isinstance(blank_project, Refusal)
    assert blank_project.message == "Name the project this change is for."
    blank_account = workspace.record_assistant_change(
        started["id"], "billing", "ordinary", "   ", False
    )
    assert isinstance(blank_account, Refusal)
    assert blank_account.message == "An account of what changed is required."
    missing_class = workspace.record_assistant_change(
        started["id"], "billing", None, "Rename the export label", False
    )
    assert isinstance(missing_class, Refusal)
    assert missing_class.message == "Choose ordinary or consequential."
    assert workspace.get_task(started["id"])["implementation_changes"] == []


def test_unknown_task_is_refused(workspace):
    refused = workspace.record_assistant_change(
        9999, "billing", "ordinary", "Rename the export label", False
    )
    assert isinstance(refused, Refusal)
    assert refused.code == 404
    assert refused.message == "Task not found."


def test_cancelled_task_cannot_take_an_assistant_change(workspace):
    started = _started(workspace)
    cancelled = workspace.transition(started["id"], "cancel", "No longer needed")
    refused = workspace.record_assistant_change(
        cancelled["id"], "billing", "ordinary", "Rename the export label", False
    )
    assert isinstance(refused, Refusal)
    assert refused.message == "A cancelled task cannot be changed. Continued work is a new task."
