from task_manager.domain.results import Refusal


def _checked(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    started = workspace.transition(ready["id"], "start")
    recorded = workspace.record_change(started["id"], "Rename the export label", "ordinary")
    criterion_id = recorded["criteria"][0]["id"]
    change_id = recorded["implementation_changes"][0]["id"]
    checked = workspace.record_check(
        recorded["id"],
        change_id,
        criterion_id,
        "The detail page shows the goal in the export",
        "Passed",
    )
    check_id = checked["implementation_changes"][0]["checks"][-1]["id"]
    return checked, check_id


def test_linked_decision_can_supersede_an_unlinked_decision(workspace):
    checked, check_id = _checked(workspace)
    task_id = checked["id"]
    first = workspace.add_decision(task_id, "Use one file", "One engineer has one workspace")
    second = workspace.add_decision(task_id, "Use one table", "Fewer joins")
    linked = workspace.add_linked_decision(
        task_id,
        "Keep the export label",
        "The check shows the goal is visible",
        check_id,
        [first["decisions"][0]["id"], second["decisions"][1]["id"]],
    )
    decisions = linked["decisions"]
    assert [item["statement"] for item in decisions] == [
        "Use one file",
        "Use one table",
        "Keep the export label",
    ]
    assert decisions[0]["check"] is None
    assert decisions[1]["check"] is None
    assert decisions[2]["check"]["id"] == check_id
    assert decisions[2]["supersedes"] == [first["decisions"][0]["id"], second["decisions"][1]["id"]]


def test_supersede_refusals_write_nothing(workspace):
    checked, check_id = _checked(workspace)
    task_id = checked["id"]
    other, _other_check = _checked(workspace, "Other")
    own = workspace.add_decision(task_id, "Use one file", "Because")
    theirs = workspace.add_decision(other["id"], "Their choice", "Different task")
    before = len(workspace.get_task(task_id)["decisions"])

    cross = workspace.add_linked_decision(
        task_id, "Keep it", "Because", check_id, [theirs["decisions"][0]["id"]]
    )
    assert isinstance(cross, Refusal)
    assert cross.code == 409
    assert cross.message == "A decision can only supersede earlier decisions on the same task."

    unknown = workspace.add_linked_decision(task_id, "Keep it", "Because", check_id, [99999])
    assert isinstance(unknown, Refusal)
    assert unknown.code == 404
    assert unknown.message == "Decision not found."

    next_id = int(
        workspace.connection.execute(
            "SELECT COALESCE(MAX(id), 0) + 1 FROM implementation_decision"
        ).fetchone()[0]
    )
    itself = workspace.add_linked_decision(task_id, "Keep it", "Because", check_id, [next_id])
    assert isinstance(itself, Refusal)
    assert itself.message == "A decision cannot supersede itself or a decision that comes after it."

    workspace.connection.execute(
        "UPDATE implementation_decision SET recorded_at = ? WHERE id = ?",
        ("2099-01-01T00:00:00Z", own["decisions"][0]["id"]),
    )
    later = workspace.add_linked_decision(
        task_id, "Keep it", "Because", check_id, [own["decisions"][0]["id"]]
    )
    assert isinstance(later, Refusal)
    assert later.message == "A decision cannot supersede itself or a decision that comes after it."
    assert len(workspace.get_task(task_id)["decisions"]) == before


def test_unlinked_decision_ignores_a_check_and_stays_off_the_parent(workspace):
    checked, check_id = _checked(workspace)
    task_id = checked["id"]
    saved = workspace.add_decision(task_id, "Use one file", "Because", None, check_id)
    assert saved["decisions"][-1]["check"] is None
    assert (
        workspace.connection.execute("SELECT COUNT(*) FROM decision_check").fetchone()[0] == 0
    )

    parent = _checked(workspace, "Parent")
    subtask = workspace.add_subtask(parent[0]["id"], "Write the checklist")
    child, child_check = _checked(workspace, "Child work")
    workspace.connection.execute(
        "UPDATE task SET parent_id = ? WHERE id = ?",
        (parent[0]["id"], child["id"]),
    )
    workspace.add_linked_decision(child["id"], "Keep the child label", "The child check passed", child_check)
    assert workspace.get_task(parent[0]["id"])["decisions"] == []
    assert workspace.get_task(child["id"])["decisions"][0]["check"]["id"] == child_check
    assert subtask["id"] != child["id"]

    ready = _checked(workspace, "Finish")
    verified = workspace.verify_criterion(
        ready[0]["id"], ready[0]["criteria"][0]["id"], "The goal is on the page.", "pass"
    )
    completed = workspace.transition(verified["id"], "complete")
    assert not isinstance(completed, Refusal)
    assert completed["status"] == "Completed"
    assert completed["decisions"] == []

    abandoned, _abandoned_check = _checked(workspace, "Abandon")
    cancelled = workspace.transition(abandoned["id"], "cancel", "Stop this work")
    assert cancelled["status"] == "Cancelled"
