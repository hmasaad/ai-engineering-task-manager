from task_manager.domain import workflow
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _read(workspace, task_id, project, title, path):
    return workspace.add_workflow_step(task_id, title, "read", str(project), path, None, None)


def _completed_reads(workspace, project, names):
    task = _in_progress(workspace)
    task_id = task["id"]
    for title, path in names:
        (project / path).write_text(path + "\n", encoding="utf-8")
        _read(workspace, task_id, project, title, path)
    for _title, _path in names:
        workspace.advance_workflow(task_id)
    return workspace.get_task(task_id)


def test_the_third_rejection_sets_the_oldest_message_aside(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    completed = _completed_reads(
        workspace,
        project,
        (("Read the note", "note.txt"), ("Read the extra", "extra.txt")),
    )
    task_id = completed["id"]
    reads = [item["path"] for item in completed["file_reads"]]
    assert [item["state"] for item in completed["workflow"]["outbox"]] == ["Pending", "Pending"]

    once = workspace.reject_outbox(task_id, "one", "The reader stopped.")
    assert once["workflow"]["dead_letters"] == []
    assert [item["state"] for item in once["workflow"]["outbox"]] == ["Pending", "Pending"]
    assert len(once["workflow"]["poison"]) == 1

    workspace.reject_outbox(task_id, "two", "The reader stopped.")
    dead = workspace.reject_outbox(task_id, "three", "The reader stopped again.")
    assert dead["status"] == "In Progress"
    assert dead["workflow"]["outbox"][0]["state"] == "Dead"
    assert dead["workflow"]["outbox"][1]["state"] == "Pending"
    assert dead["workflow"]["dead_letters"] == [
        {
            "outbox_id": dead["workflow"]["outbox"][0]["id"],
            "title": "Read the note",
            "effect": "note.txt",
            "reason": "The reader stopped again.",
        }
    ]
    assert [item["path"] for item in dead["file_reads"]] == reads

    delivered = workspace.deliver_outbox(task_id, "ship")
    assert [item["state"] for item in delivered["workflow"]["outbox"]] == ["Dead", "Delivered"]
    assert [item["path"] for item in delivered["file_reads"]] == reads


def test_one_rejection_still_allows_delivery(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    completed = _completed_reads(workspace, project, (("Read the note", "note.txt"),))
    task_id = completed["id"]
    rejected = workspace.reject_outbox(task_id, "once", "The reader stopped.")
    delivered = workspace.deliver_outbox(task_id, "ship")
    assert delivered["workflow"]["outbox"][0]["state"] == "Delivered"
    assert delivered["workflow"]["poison"] == rejected["workflow"]["poison"]
    assert delivered["workflow"]["dead_letters"] == []


def test_a_rejection_is_counted_once(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    completed = _completed_reads(workspace, project, (("Read the note", "note.txt"),))
    task_id = completed["id"]
    blank_name = workspace.reject_outbox(task_id, " ", "The reader stopped.")
    assert isinstance(blank_name, Refusal)
    assert blank_name.message == "Name this rejection."
    blank_reason = workspace.reject_outbox(task_id, "once", " ")
    assert blank_reason.message == "Name why this message is poison."
    assert workspace.get_task(task_id)["workflow"]["poison"] == []

    once = workspace.reject_outbox(task_id, "once", "The reader stopped.")
    repeated = workspace.reject_outbox(task_id, "once", "A different reason.")
    assert repeated["workflow"]["poison"] == once["workflow"]["poison"]
    assert repeated["workflow"]["outbox"][0]["state"] == "Pending"

    other = _completed_reads(workspace, project, (("Read the extra", "extra.txt"),))
    other_rejected = workspace.reject_outbox(other["id"], "once", "The reader stopped.")
    assert len(other_rejected["workflow"]["poison"]) == 1
    assert len(workspace.get_task(task_id)["workflow"]["poison"]) == 1

    workspace.deliver_outbox(task_id, "ship")
    empty = workspace.reject_outbox(task_id, "next", "The reader stopped.")
    assert empty.message == "There is no outbox message to reject."


def test_a_rolled_back_rejection_stores_nothing(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    completed = _completed_reads(workspace, project, (("Read the note", "note.txt"),))
    task_id = completed["id"]

    def _reject_then_refuse(connection):
        workflow.reject(
            connection, task_id, "once", "The reader stopped.", "2026-10-16T00:00:00Z"
        )
        return bad_request("no")

    refused = call_in_transaction(workspace.connection, _reject_then_refuse)
    assert refused.message == "no"
    opened = workspace.get_task(task_id)
    assert opened["workflow"]["poison"] == []
    assert opened["workflow"]["dead_letters"] == []
    assert opened["workflow"]["outbox"][0]["state"] == "Pending"
