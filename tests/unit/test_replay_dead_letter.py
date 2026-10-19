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
    (project / path).write_text(path + "\n", encoding="utf-8")
    return workspace.add_workflow_step(task_id, title, "read", str(project), path, None, None)


def _dead(workspace, project, names=(("Read the note", "note.txt"),)):
    task = _in_progress(workspace)
    task_id = task["id"]
    for title, path in names:
        _read(workspace, task_id, project, title, path)
    for _title, _path in names:
        workspace.advance_workflow(task_id)
    for index in range(len(names) * 3):
        workspace.reject_outbox(task_id, f"reject-{index}", "The reader stopped.")
    return workspace.get_task(task_id)


def test_a_replay_returns_the_oldest_dead_letter(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    dead = _dead(workspace, project, (("Read the note", "note.txt"), ("Read the extra", "extra.txt")))
    task_id = dead["id"]
    reads = [item["path"] for item in dead["file_reads"]]
    assert [item["state"] for item in dead["workflow"]["outbox"]] == ["Dead", "Dead"]

    returned = workspace.replay_dead_letter(task_id, "once")
    assert returned["status"] == "In Progress"
    assert [item["state"] for item in returned["workflow"]["outbox"]] == ["Pending", "Dead"]
    assert returned["workflow"]["dead_letters"][0]["reason"] == "The reader stopped."
    assert returned["workflow"]["dead_letter_replays"] == [
        {
            "name": "once",
            "outbox_id": returned["workflow"]["outbox"][0]["id"],
            "title": "Read the note",
        }
    ]
    assert [item["path"] for item in returned["file_reads"]] == reads

    repeated = workspace.replay_dead_letter(task_id, " once ")
    assert repeated["workflow"]["dead_letter_replays"] == returned["workflow"]["dead_letter_replays"]
    assert [item["state"] for item in repeated["workflow"]["outbox"]] == ["Pending", "Dead"]

    delivered = workspace.deliver_outbox(task_id, "ship")
    assert [item["state"] for item in delivered["workflow"]["outbox"]] == ["Delivered", "Dead"]
    assert [item["path"] for item in delivered["file_reads"]] == reads
    again = workspace.deliver_outbox(task_id, "ship")
    assert again["workflow"]["inbox"] == delivered["workflow"]["inbox"]

    nxt = workspace.replay_dead_letter(task_id, "next")
    assert [item["state"] for item in nxt["workflow"]["outbox"]] == ["Delivered", "Pending"]
    assert len(nxt["workflow"]["dead_letter_replays"]) == 2


def test_a_replay_does_not_reset_attempts(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")
    completed = workspace.advance_workflow(task_id)
    outbox_id = completed["workflow"]["outbox"][0]["id"]
    for name, at in (
        ("one", "2026-10-19T00:00:00Z"),
        ("two", "2026-10-19T00:01:00Z"),
        ("three", "2026-10-19T00:02:00Z"),
    ):
        call_in_transaction(
            workspace.connection,
            lambda connection, kept=name, when=at: workflow.record_retry(
                connection, task_id, kept, when
            ),
        )
    counted = workspace.get_task(task_id)
    assert counted["workflow"]["retries"][0]["attempt_count"] == 3
    assert counted["workflow"]["outbox"][0]["state"] == "Dead"

    returned = workspace.replay_dead_letter(task_id, "back")
    assert returned["workflow"]["retries"][0]["attempt_count"] == 3
    assert returned["workflow"]["outbox"][0]["state"] == "Pending"
    delivered = workspace.deliver_outbox(task_id, "ship")
    assert delivered["workflow"]["outbox"][0]["state"] == "Delivered"
    stored = workspace.connection.execute(
        "SELECT state FROM workflow_outbox WHERE id = ?",
        (outbox_id,),
    ).fetchone()
    assert stored["state"] == "Delivered"


def test_a_rolled_back_replay_leaves_the_message_dead(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    dead = _dead(workspace, project)
    task_id = dead["id"]

    blank = workspace.replay_dead_letter(task_id, "  ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this replay."

    def _then_refuse(connection):
        workflow.replay_dead_letter(connection, task_id, "once", "2026-10-19T00:00:00Z")
        return bad_request("no")

    rolled = call_in_transaction(workspace.connection, _then_refuse)
    assert isinstance(rolled, Refusal)
    opened = workspace.get_task(task_id)
    assert opened["workflow"]["outbox"][0]["state"] == "Dead"
    assert opened["workflow"]["dead_letter_replays"] == []
    skipped = workspace.deliver_outbox(task_id, "ship")
    assert isinstance(skipped, Refusal)
    assert skipped.message == "There is no outbox message to deliver."

    returned = workspace.replay_dead_letter(task_id, "once")
    assert returned["workflow"]["outbox"][0]["state"] == "Pending"
    missing = workspace.replay_dead_letter(task_id, "other")
    assert isinstance(missing, Refusal)
    assert missing.message == "There is no dead letter to replay."

    other = _dead(workspace, project, (("Read the extra", "extra.txt"),))
    other_returned = workspace.replay_dead_letter(other["id"], "once")
    assert other_returned["workflow"]["dead_letter_replays"][0]["title"] == "Read the extra"

    draft = workspace.create_task("Draft")
    refused = workspace.replay_dead_letter(draft["id"], "later")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
