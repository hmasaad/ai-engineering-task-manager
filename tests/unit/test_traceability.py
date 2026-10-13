def _task(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    return workspace.add_criterion(created["id"], "The export contains the goal")


def test_tasks_without_a_requirement_and_unverified_criteria_are_listed(workspace):
    task = _task(workspace)
    child = workspace.add_subtask(task["id"], "Write the export")
    listed = workspace.traceability()
    assert listed["tasks_without_requirement"] == [
        {"id": task["id"], "title": "Add export", "status": "Draft"},
        {"id": child["id"], "title": "Write the export", "status": "Draft"},
    ]
    assert listed["criteria_without_verification"] == [
        {
            "id": task["criteria"][0]["id"],
            "task_id": task["id"],
            "task_title": "Add export",
            "text": "The export contains the goal",
        }
    ]
    assert workspace.list_requirements() == []

    requirement = workspace.record_requirement("No task yet", "functional")
    assert workspace.list_requirements()[0]["missing"] == [
        "Missing a task",
        "Missing an acceptance criterion",
        "Missing a check",
    ]

    linked = workspace.record_requirement("The export contains the goal", "functional")
    workspace.link_requirement_task(linked["id"], task["id"])
    after_link = workspace.traceability()
    assert [item["id"] for item in after_link["tasks_without_requirement"]] == [child["id"]]
    assert after_link["criteria_without_verification"][0]["id"] == task["criteria"][0]["id"]

    ready = workspace.transition(task["id"], "mark_ready")
    started = workspace.transition(ready["id"], "start")
    verified = workspace.verify_criterion(
        started["id"],
        task["criteria"][0]["id"],
        "The export contains the goal",
        "pass",
        "inspection",
        "local-1",
    )
    assert verified["criteria"][0]["id"] not in {
        item["id"] for item in workspace.traceability()["criteria_without_verification"]
    }

    workspace.unverify_criterion(started["id"], task["criteria"][0]["id"])
    assert task["criteria"][0]["id"] in {
        item["id"] for item in workspace.traceability()["criteria_without_verification"]
    }


def test_a_cancelled_task_without_a_requirement_is_listed(workspace):
    created = workspace.create_task("Add export")
    cancelled = workspace.transition(created["id"], "cancel", "Not needed")
    listed = workspace.traceability()["tasks_without_requirement"]
    assert listed == [{"id": cancelled["id"], "title": "Add export", "status": "Cancelled"}]
