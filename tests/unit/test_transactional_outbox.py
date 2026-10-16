from task_manager.domain import workflow
from task_manager.domain.results import bad_request
from task_manager.storage import workflow_store
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _read(workspace, task_id, project, title, path):
    return workspace.add_workflow_step(task_id, title, "read", str(project), path, None, None)


def test_a_completed_step_stores_one_outbox_message(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    assert task["workflow"]["outbox"] == []
    _read(workspace, task_id, project, "Read the note", "note.txt")
    completed = workspace.advance_workflow(task_id)
    assert completed["workflow"]["outbox"] == [
        {
            "id": completed["workflow"]["outbox"][0]["id"],
            "title": "Read the note",
            "effect": "note.txt",
            "state": "Pending",
        }
    ]
    assert len(completed["file_reads"]) == 1
    step_id = completed["workflow"]["steps"][0]["id"]

    def _complete_again(connection):
        step = workflow_store.row_step(connection, step_id)
        workflow._set_outcome(
            connection, step, "Completed", None, None, "2026-10-16T00:00:01Z"
        )

    call_in_transaction(workspace.connection, _complete_again)
    again = workspace.get_task(task_id)
    assert again["workflow"]["outbox"] == completed["workflow"]["outbox"]

    missing = _in_progress(workspace, "Read a missing file")
    missing_id = missing["id"]
    _read(workspace, missing_id, project, "Read the gap", "missing.txt")
    failed = workspace.advance_workflow(missing_id)
    assert failed["workflow"]["steps"][0]["state"] == "Failed"
    assert failed["workflow"]["outbox"] == []


def test_a_rolled_back_completion_stores_no_message(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    added = _read(workspace, task_id, project, "Read the note", "note.txt")
    step_id = added["workflow"]["steps"][0]["id"]
    step = workflow_store.row_step(workspace.connection, step_id)

    def _complete_then_refuse(connection):
        workflow._set_outcome(
            connection, step, "Completed", None, None, "2026-10-16T00:00:00Z"
        )
        return bad_request("no")

    refused = call_in_transaction(workspace.connection, _complete_then_refuse)
    assert refused.message == "no"
    opened = workspace.get_task(task_id)
    assert opened["workflow"]["steps"][0]["state"] == "Pending"
    assert opened["workflow"]["outbox"] == []
    assert opened["file_reads"] == []


def test_a_delivery_name_is_accepted_once(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    (project / "extra.txt").write_text("extra\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    assert workspace.deliver_outbox(task_id, "once").message == (
        "There is no outbox message to deliver."
    )
    _read(workspace, task_id, project, "Read the note", "note.txt")
    _read(workspace, task_id, project, "Read the extra", "extra.txt")
    workspace.advance_workflow(task_id)
    ready = workspace.advance_workflow(task_id)
    blank = workspace.deliver_outbox(task_id, " ")
    assert blank.message == "Name this delivery."
    assert [item["state"] for item in workspace.get_task(task_id)["workflow"]["outbox"]] == [
        "Pending",
        "Pending",
    ]
    delivered = workspace.deliver_outbox(task_id, "once")
    assert [item["state"] for item in delivered["workflow"]["outbox"]] == [
        "Delivered",
        "Pending",
    ]
    assert delivered["workflow"]["inbox"] == [
        {"name": "once", "outbox_id": delivered["workflow"]["outbox"][0]["id"]}
    ]
    assert delivered["status"] == "In Progress"
    repeated = workspace.deliver_outbox(task_id, "once")
    assert [item["state"] for item in repeated["workflow"]["outbox"]] == [
        "Delivered",
        "Pending",
    ]
    assert repeated["workflow"]["inbox"] == delivered["workflow"]["inbox"]
    followed = workspace.deliver_outbox(task_id, "next")
    assert [item["state"] for item in followed["workflow"]["outbox"]] == [
        "Delivered",
        "Delivered",
    ]
    assert [item["path"] for item in followed["file_reads"]] == ["note.txt", "extra.txt"]
    assert len(ready["workflow"]["replay"]) == len(followed["workflow"]["replay"])

    other = _in_progress(workspace, "Read elsewhere")
    other_id = other["id"]
    _read(workspace, other_id, project, "Read the note", "note.txt")
    workspace.advance_workflow(other_id)
    other_delivered = workspace.deliver_outbox(other_id, "once")
    assert other_delivered["workflow"]["outbox"][0]["state"] == "Delivered"
    assert other_delivered["workflow"]["inbox"][0]["name"] == "once"
