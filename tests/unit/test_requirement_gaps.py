def test_the_gap_list_names_what_is_missing(workspace):
    unlinked = workspace.record_requirement("No task yet", "functional")
    task_only = workspace.record_requirement("Task only", "functional")
    task = workspace.create_task("Add export")
    workspace.link_requirement_task(task_only["id"], task["id"])
    named = workspace.record_requirement("Needs a pass", "non-functional")
    workspace.link_requirement_task(named["id"], task["id"])
    workspace.set_goal(task["id"], "Take the record")
    task = workspace.add_criterion(task["id"], "The export contains the goal")
    workspace.link_requirement_criterion(named["id"], task["id"], task["criteria"][0]["id"])
    workspace.name_requirement_check(named["id"], "export shows the goal")
    done = workspace.record_requirement("Ready", "functional")
    workspace.link_requirement_task(done["id"], task["id"])
    workspace.link_requirement_criterion(done["id"], task["id"], task["criteria"][0]["id"])
    workspace.name_requirement_check(done["id"], "export shows the goal")
    workspace.record_requirement_run(done["id"], "export shows the goal", "Passed", "local-1")

    listed = {item["identifier"]: item["missing"] for item in workspace.list_requirements()}
    assert listed["REQ-1"] == [
        "Missing a task",
        "Missing an acceptance criterion",
        "Missing a check",
    ]
    assert listed["REQ-2"] == ["Missing an acceptance criterion", "Missing a check"]
    assert listed["REQ-3"] == ["Missing a passing result for export shows the goal"]
    assert listed["REQ-4"] == []
    assert unlinked["identifier"] == "REQ-1"


def test_old_tasks_are_not_requirements(workspace):
    workspace.create_task("Add export")
    assert workspace.list_requirements() == []
