from task_manager.clock import format_time
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


def _completed(workspace, project, title="Read the note", path="note.txt"):
    task = _in_progress(workspace)
    task_id = task["id"]
    (project / path).write_text("hello\n", encoding="utf-8")
    _read(workspace, task_id, project, title, path)
    return workspace.advance_workflow(task_id)


def _until(workspace, target):
    while format_time(workspace.clock.now()) < target:
        pass


def test_an_early_delivery_does_not_count(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    completed = _completed(workspace, project)
    task_id = completed["id"]
    reads = [item["path"] for item in completed["file_reads"]]
    attempted = workspace.retry_delivery(task_id, "once")
    assert attempted["status"] == "In Progress"
    assert attempted["workflow"]["outbox"][0]["state"] == "Pending"
    assert attempted["workflow"]["retries"] == [
        {
            "outbox_id": attempted["workflow"]["outbox"][0]["id"],
            "attempt_count": 1,
            "next_eligible_at": attempted["workflow"]["retries"][0]["next_eligible_at"],
        }
    ]
    assert attempted["workflow"]["inbox"] == []
    assert [item["path"] for item in attempted["file_reads"]] == reads

    repeated = workspace.retry_delivery(task_id, " once ")
    assert repeated["workflow"]["retries"][0]["attempt_count"] == 1

    early = workspace.deliver_outbox(task_id, "ship")
    assert isinstance(early, Refusal)
    assert early.message == "This delivery is not due yet."
    assert workspace.get_task(task_id)["workflow"]["outbox"][0]["state"] == "Pending"
    assert workspace.get_task(task_id)["workflow"]["retries"][0]["attempt_count"] == 1
    assert workspace.get_task(task_id)["workflow"]["inbox"] == []

    _until(workspace, attempted["workflow"]["retries"][0]["next_eligible_at"])
    delivered = workspace.deliver_outbox(task_id, "ship")
    assert delivered["workflow"]["outbox"][0]["state"] == "Delivered"
    assert delivered["workflow"]["retries"][0]["attempt_count"] == 1
    assert delivered["workflow"]["inbox"] == [
        {"name": "ship", "outbox_id": delivered["workflow"]["outbox"][0]["id"]}
    ]
    again = workspace.deliver_outbox(task_id, "ship")
    assert again["workflow"]["inbox"] == delivered["workflow"]["inbox"]

    blank = workspace.retry_delivery(task_id, "  ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this attempt."
    missing = workspace.retry_delivery(task_id, "later")
    assert isinstance(missing, Refusal)
    assert missing.message == "There is no outbox message to retry."


def test_the_third_attempt_writes_one_dead_letter(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    completed = _completed(workspace, project)
    task_id = completed["id"]
    outbox_id = completed["workflow"]["outbox"][0]["id"]
    reads = [item["path"] for item in completed["file_reads"]]

    first = workspace.retry_delivery(task_id, "one")
    _until(workspace, first["workflow"]["retries"][0]["next_eligible_at"])
    second = workspace.retry_delivery(task_id, "two")
    assert second["workflow"]["retries"][0]["attempt_count"] == 2
    assert second["workflow"]["dead_letters"] == []
    due = second["workflow"]["retries"][0]["next_eligible_at"]

    def _third_then_refuse(connection):
        workflow.record_retry(connection, task_id, "three", due)
        return bad_request("no")

    rolled = call_in_transaction(workspace.connection, _third_then_refuse)
    assert isinstance(rolled, Refusal)
    opened = workspace.get_task(task_id)
    assert opened["workflow"]["retries"][0]["attempt_count"] == 2
    assert opened["workflow"]["dead_letters"] == []
    stored = workspace.connection.execute(
        "SELECT state FROM workflow_outbox WHERE id = ?",
        (outbox_id,),
    ).fetchone()
    assert stored["state"] == "Pending"

    _until(workspace, due)
    third = workspace.retry_delivery(task_id, "three")
    assert third["workflow"]["retries"][0]["attempt_count"] == 3
    assert third["workflow"]["outbox"][0]["state"] == "Dead"
    assert third["workflow"]["dead_letters"] == [
        {
            "outbox_id": outbox_id,
            "title": "Read the note",
            "effect": "note.txt",
            "reason": "The delivery was attempted too many times.",
        }
    ]
    assert [item["path"] for item in third["file_reads"]] == reads
    stored = workspace.connection.execute(
        "SELECT state FROM workflow_outbox WHERE id = ?",
        (outbox_id,),
    ).fetchone()
    assert stored["state"] == "Pending"
    blocked = workspace.deliver_outbox(task_id, "ship")
    assert isinstance(blocked, Refusal)
    assert blocked.message == "There is no outbox message to deliver."

    other = _completed(workspace, project, "Read the extra", "extra.txt")
    other_attempt = workspace.retry_delivery(other["id"], "one")
    assert other_attempt["workflow"]["retries"][0]["attempt_count"] == 1

    draft = workspace.create_task("Draft")
    refused = workspace.retry_delivery(draft["id"], "later")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
