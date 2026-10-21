from task_manager.domain import allocation
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _agent(name):
    return {"name": name}


def _yield(name, agent, value):
    return {"name": name, "agent": agent, "value": value}


def _share(agent, units):
    return {"agent": agent, "units": units}


def test_an_agent_is_named_once(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    named = workspace.name_allocation_agent(task_id, " ada ")
    assert named["status"] == "In Progress"
    assert named["allocation"]["agents"] == [_agent("ada")]
    assert named["file_reads"] == []
    assert named["workflow"]["steps"] == []
    assert named["fidelity"]["candidates"] == []
    repeated = workspace.name_allocation_agent(task_id, "ada")
    assert repeated["allocation"]["agents"] == [_agent("ada")]
    for name in ("grace", "mina", "nora"):
        workspace.name_allocation_agent(task_id, name)
    assert [item["name"] for item in workspace.get_task(task_id)["allocation"]["agents"]] == [
        "ada",
        "grace",
        "mina",
        "nora",
    ]

    other = _in_progress(workspace, "Other agent")
    other_named = workspace.name_allocation_agent(other["id"], "ada")
    assert other_named["allocation"]["agents"] == [_agent("ada")]

    blank = workspace.name_allocation_agent(task_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this agent."
    fifth = workspace.name_allocation_agent(task_id, "otis")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 agents."
    assert len(workspace.get_task(task_id)["allocation"]["agents"]) == 4

    draft = workspace.create_task("Draft")
    refused = workspace.name_allocation_agent(draft["id"], "ada")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["allocation"]["agents"] == []


def test_a_yield_keeps_its_value(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_allocation_agent(task_id, "ada")
    recorded = workspace.record_yield(task_id, " one ", " ada ", "2")
    assert recorded["allocation"]["yields"] == [_yield("one", "ada", 2)]
    repeated = workspace.record_yield(task_id, "one", "ada", "1")
    assert repeated["allocation"]["yields"] == recorded["allocation"]["yields"]
    unchanged = workspace.record_yield(task_id, "one", " ", "3")
    assert unchanged["allocation"]["yields"] == recorded["allocation"]["yields"]

    missing = workspace.record_yield(task_id, "two", "grace", "1")
    assert isinstance(missing, Refusal)
    assert missing.message == "That agent is not on this task."
    again = workspace.record_yield(task_id, "two", "ada", "1")
    assert isinstance(again, Refusal)
    assert again.message == "That agent already has a yield."
    blank = workspace.record_yield(task_id, " ", "ada", "1")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this yield."
    blank_agent = workspace.record_yield(task_id, "two", " ", "1")
    assert isinstance(blank_agent, Refusal)
    assert blank_agent.message == "Name the agent."
    bad_value = workspace.record_yield(task_id, "two", "ada", "3")
    assert isinstance(bad_value, Refusal)
    assert bad_value.message == "Name a yield of 1 or 2."
    assert len(workspace.get_task(task_id)["allocation"]["yields"]) == 1

    full = _in_progress(workspace, "Full yields")
    full_id = full["id"]
    for name in ("ada", "grace", "mina", "nora"):
        workspace.name_allocation_agent(full_id, name)
        workspace.record_yield(full_id, name, name, "1")
    fifth = workspace.record_yield(full_id, "five", "ada", "2")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 yields."
    assert len(workspace.get_task(full_id)["allocation"]["yields"]) == 4


def test_the_shares_follow_the_yield(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_allocation_agent(task_id, "ada")
    workspace.name_allocation_agent(task_id, "grace")
    workspace.record_yield(task_id, "one", "ada", "2")
    workspace.record_yield(task_id, "two", "grace", "1")

    allocated = workspace.allocate_pool(task_id)
    assert allocated["status"] == "In Progress"
    assert allocated["allocation"]["shares"] == [_share("ada", 3), _share("grace", 1)]
    assert sum(item["units"] for item in allocated["allocation"]["shares"]) == 4
    assert allocated["bandit"]["actions"] == []

    kept = workspace.record_yield(task_id, "three", "ada", "1")
    assert isinstance(kept, Refusal)
    assert kept.message == "That agent already has a yield."
    assert workspace.get_task(task_id)["allocation"]["shares"] == [
        _share("ada", 3),
        _share("grace", 1),
    ]

    tied = _in_progress(workspace, "Tied yields")
    tied_id = tied["id"]
    workspace.name_allocation_agent(tied_id, "ada")
    workspace.name_allocation_agent(tied_id, "grace")
    workspace.record_yield(tied_id, "one", "ada", "2")
    workspace.record_yield(tied_id, "two", "grace", "2")
    assert workspace.allocate_pool(tied_id)["allocation"]["shares"] == [
        _share("ada", 2),
        _share("grace", 2),
    ]

    alone = _in_progress(workspace, "One agent")
    alone_id = alone["id"]
    workspace.name_allocation_agent(alone_id, "ada")
    workspace.record_yield(alone_id, "one", "ada", "1")
    assert workspace.allocate_pool(alone_id)["allocation"]["shares"] == [_share("ada", 4)]

    wide = _in_progress(workspace, "Four agents")
    wide_id = wide["id"]
    for name, value in (("ada", "2"), ("grace", "1"), ("mina", "1"), ("nora", "1")):
        workspace.name_allocation_agent(wide_id, name)
        workspace.record_yield(wide_id, name, name, value)
    assert workspace.allocate_pool(wide_id)["allocation"]["shares"] == [
        _share("ada", 2),
        _share("grace", 1),
        _share("mina", 1),
        _share("nora", 0),
    ]

    empty = _in_progress(workspace, "Empty allocation")
    empty_id = empty["id"]
    missing = workspace.allocate_pool(empty_id)
    assert isinstance(missing, Refusal)
    assert missing.message == "Name an agent first."
    workspace.name_allocation_agent(empty_id, "ada")
    workspace.name_allocation_agent(empty_id, "grace")
    workspace.record_yield(empty_id, "one", "ada", "2")
    waiting = workspace.allocate_pool(empty_id)
    assert isinstance(waiting, Refusal)
    assert waiting.message == "Record a yield for every agent first."

    cleared = workspace.name_allocation_agent(task_id, "mina")
    assert cleared["allocation"]["shares"] == []

    draft = workspace.create_task("Draft")
    draft_refused = workspace.allocate_pool(draft["id"])
    assert isinstance(draft_refused, Refusal)
    assert draft_refused.message == "The task must be In Progress."

    fresh = _in_progress(workspace, "Rollback")
    fresh_id = fresh["id"]
    workspace.name_allocation_agent(fresh_id, "ada")
    workspace.name_allocation_agent(fresh_id, "grace")
    workspace.record_yield(fresh_id, "one", "ada", "2")
    workspace.record_yield(fresh_id, "two", "grace", "1")
    stored = workspace.allocate_pool(fresh_id)
    assert stored["allocation"]["shares"] == [_share("ada", 3), _share("grace", 1)]

    def rolled(connection):
        allocation.name_agent(connection, fresh_id, "mina", "2026-10-21T00:00:00Z")
        allocation.allocate(connection, fresh_id, "2026-10-21T00:00:00Z")
        return bad_request("stop")

    assert isinstance(call_in_transaction(workspace.connection, rolled), Refusal)
    restored = workspace.get_task(fresh_id)
    assert [item["name"] for item in restored["allocation"]["agents"]] == ["ada", "grace"]
    assert restored["allocation"]["shares"] == [_share("ada", 3), _share("grace", 1)]
