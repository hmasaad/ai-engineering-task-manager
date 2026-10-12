def test_opening_a_requirement_does_not_record_another_run(workspace):
    task = workspace.create_task("Add export")
    workspace.set_goal(task["id"], "Take the record")
    task = workspace.add_criterion(task["id"], "The export contains the goal")
    workspace.transition(task["id"], "mark_ready")
    task = workspace.transition(task["id"], "start")
    requirement = workspace.record_requirement("The export contains the goal", "functional")
    workspace.link_requirement_task(requirement["id"], task["id"])
    requirement = workspace.link_requirement_criterion(
        requirement["id"], task["id"], task["criteria"][0]["id"]
    )
    workspace.name_requirement_check(requirement["id"], "export shows the goal")
    recorded = workspace.record_requirement_run(
        requirement["id"], "export shows the goal", "Passed", "local-1"
    )
    opened = workspace.get_requirement(requirement["id"])
    task_again = workspace.get_task(task["id"])
    assert opened["checks"][0]["runs"] == recorded["checks"][0]["runs"]
    assert opened["checks"][0]["current_result"] == "Passed"
    assert task_again["requirements"][0]["identifier"] == opened["identifier"]
    assert len(opened["checks"][0]["runs"]) == 1
