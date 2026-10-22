from task_manager.domain import consensus
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _point(name, setting):
    return {"name": name, "setting": setting}


def _name(name):
    return {"name": name}


def _report(name, node, point, score):
    return {"name": name, "node": node, "point": point, "score": score}


def _proposal(node, point):
    return {"node": node, "point": point}


def _choice(point, node, suggestions):
    return {"point": point, "node": node, "suggestions": suggestions}


def test_a_point_and_a_node_are_named_once(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    named = workspace.name_consensus_point(task_id, " ada ", "1")
    assert named["status"] == "In Progress"
    assert named["consensus"]["points"] == [_point("ada", 1)]
    assert named["file_reads"] == []
    assert named["workflow"]["steps"] == []
    assert named["hyperband"]["trials"] == []
    repeated = workspace.name_consensus_point(task_id, "ada", "2")
    assert repeated["consensus"]["points"] == [_point("ada", 1)]
    kept = workspace.name_consensus_point(task_id, "ada", " ")
    assert kept["consensus"]["points"] == [_point("ada", 1)]
    node = workspace.name_consensus_node(task_id, " north ")
    assert node["consensus"]["nodes"] == [_name("north")]
    again = workspace.name_consensus_node(task_id, "north")
    assert again["consensus"]["nodes"] == [_name("north")]
    workspace.name_consensus_point(task_id, "grace", "2")
    workspace.name_consensus_point(task_id, "mina", "1")
    workspace.name_consensus_point(task_id, "nora", "2")
    assert [item["name"] for item in workspace.get_task(task_id)["consensus"]["points"]] == [
        "ada",
        "grace",
        "mina",
        "nora",
    ]
    workspace.name_consensus_node(task_id, "south")

    other = _in_progress(workspace, "Other point")
    other_named = workspace.name_consensus_point(other["id"], "ada", "2")
    assert other_named["consensus"]["points"] == [_point("ada", 2)]

    blank = workspace.name_consensus_point(task_id, " ", "1")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this point."
    blank_node = workspace.name_consensus_node(task_id, " ")
    assert isinstance(blank_node, Refusal)
    assert blank_node.message == "Name this node."
    bad_setting = workspace.name_consensus_point(task_id, "teal", "3")
    assert isinstance(bad_setting, Refusal)
    assert bad_setting.message == "Name a setting of 1 or 2."
    fifth = workspace.name_consensus_point(task_id, "teal", "1")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 points."
    third = workspace.name_consensus_node(task_id, "east")
    assert isinstance(third, Refusal)
    assert third.message == "This task already has 2 nodes."
    assert len(workspace.get_task(task_id)["consensus"]["points"]) == 4
    assert len(workspace.get_task(task_id)["consensus"]["nodes"]) == 2

    draft = workspace.create_task("Draft")
    refused = workspace.name_consensus_point(draft["id"], "ada", "1")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["consensus"]["points"] == []


def test_a_report_keeps_its_score(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_consensus_point(task_id, "ada", "1")
    workspace.name_consensus_node(task_id, "north")
    recorded = workspace.record_consensus_report(task_id, " one ", " north ", " ada ", "2")
    assert recorded["consensus"]["reports"] == [_report("one", "north", "ada", 2)]
    repeated = workspace.record_consensus_report(task_id, "one", "north", "ada", "1")
    assert repeated["consensus"]["reports"] == recorded["consensus"]["reports"]
    unchanged = workspace.record_consensus_report(task_id, "one", " ", " ", " ")
    assert unchanged["consensus"]["reports"] == recorded["consensus"]["reports"]

    missing_node = workspace.record_consensus_report(task_id, "two", "east", "ada", "1")
    assert isinstance(missing_node, Refusal)
    assert missing_node.message == "That node is not on this task."
    missing_point = workspace.record_consensus_report(task_id, "two", "north", "teal", "1")
    assert isinstance(missing_point, Refusal)
    assert missing_point.message == "That point is not on this task."
    again = workspace.record_consensus_report(task_id, "two", "north", "ada", "1")
    assert isinstance(again, Refusal)
    assert again.message == "That node already reported this point."
    blank = workspace.record_consensus_report(task_id, " ", "north", "ada", "1")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this report."
    blank_node = workspace.record_consensus_report(task_id, "two", " ", "ada", "1")
    assert isinstance(blank_node, Refusal)
    assert blank_node.message == "Name the node."
    blank_point = workspace.record_consensus_report(task_id, "two", "north", " ", "1")
    assert isinstance(blank_point, Refusal)
    assert blank_point.message == "Name the point."
    bad_score = workspace.record_consensus_report(task_id, "two", "north", "ada", " ")
    assert isinstance(bad_score, Refusal)
    assert bad_score.message == "Name a score of 1 or 2."
    assert len(workspace.get_task(task_id)["consensus"]["reports"]) == 1

    full = _in_progress(workspace, "Full reports")
    full_id = full["id"]
    workspace.name_consensus_point(full_id, "ada", "1")
    workspace.name_consensus_point(full_id, "grace", "2")
    workspace.name_consensus_node(full_id, "north")
    workspace.name_consensus_node(full_id, "south")
    workspace.record_consensus_report(full_id, "one", "north", "ada", "2")
    workspace.record_consensus_report(full_id, "two", "south", "ada", "1")
    workspace.record_consensus_report(full_id, "three", "north", "grace", "1")
    workspace.record_consensus_report(full_id, "four", "south", "grace", "2")
    fifth = workspace.record_consensus_report(full_id, "five", "north", "ada", "1")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 reports."
    assert len(workspace.get_task(full_id)["consensus"]["reports"]) == 4


def test_the_nodes_agree_on_the_nearest_point(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_consensus_point(task_id, "ada", "1")
    workspace.name_consensus_point(task_id, "grace", "2")
    workspace.name_consensus_point(task_id, "mina", "1")
    workspace.name_consensus_node(task_id, "north")
    workspace.name_consensus_node(task_id, "south")
    workspace.record_consensus_report(task_id, "one", "north", "ada", "2")
    workspace.record_consensus_report(task_id, "two", "south", "ada", "1")

    agreed = workspace.agree_consensus(task_id)
    assert agreed["status"] == "In Progress"
    assert agreed["consensus"]["proposals"] == [
        _proposal("north", "mina"),
        _proposal("south", "mina"),
    ]
    assert agreed["consensus"]["choice"] == _choice("mina", "north", 2)
    assert agreed["fidelity"]["candidates"] == []
    assert agreed["allocation"]["agents"] == []
    repeated = workspace.agree_consensus(task_id)
    assert repeated["consensus"]["choice"] == _choice("mina", "north", 2)

    workspace.record_consensus_report(task_id, "three", "north", "grace", "1")
    cleared = workspace.get_task(task_id)
    assert cleared["consensus"]["proposals"] == []
    assert cleared["consensus"]["choice"] is None
    kept = workspace.record_consensus_report(task_id, "three", "south", "grace", "2")
    assert kept["consensus"]["choice"] is None

    split = _in_progress(workspace, "Split suggestions")
    split_id = split["id"]
    workspace.name_consensus_point(split_id, "ada", "1")
    workspace.name_consensus_point(split_id, "grace", "2")
    workspace.name_consensus_point(split_id, "mina", "1")
    workspace.name_consensus_node(split_id, "north")
    workspace.name_consensus_node(split_id, "south")
    workspace.record_consensus_report(split_id, "one", "north", "ada", "2")
    workspace.record_consensus_report(split_id, "two", "south", "grace", "2")
    divided = workspace.agree_consensus(split_id)
    assert divided["consensus"]["proposals"] == [
        _proposal("north", "mina"),
        _proposal("south", "ada"),
    ]
    assert divided["consensus"]["choice"] == _choice("ada", "south", 1)

    quiet = _in_progress(workspace, "Quiet node")
    quiet_id = quiet["id"]
    workspace.name_consensus_point(quiet_id, "ada", "1")
    workspace.name_consensus_point(quiet_id, "grace", "2")
    workspace.name_consensus_point(quiet_id, "mina", "1")
    workspace.name_consensus_node(quiet_id, "north")
    workspace.name_consensus_node(quiet_id, "south")
    workspace.record_consensus_report(quiet_id, "one", "north", "ada", "2")
    silent = workspace.agree_consensus(quiet_id)
    assert silent["consensus"]["proposals"] == [
        _proposal("north", "mina"),
        _proposal("south", "ada"),
    ]
    assert silent["consensus"]["choice"] == _choice("ada", "south", 1)

    nearest = _in_progress(workspace, "Nearest point")
    nearest_id = nearest["id"]
    workspace.name_consensus_point(nearest_id, "ada", "1")
    workspace.name_consensus_point(nearest_id, "grace", "2")
    workspace.name_consensus_point(nearest_id, "mina", "1")
    workspace.name_consensus_point(nearest_id, "nora", "2")
    workspace.name_consensus_node(nearest_id, "north")
    workspace.name_consensus_node(nearest_id, "south")
    workspace.record_consensus_report(nearest_id, "one", "north", "grace", "2")
    workspace.record_consensus_report(nearest_id, "two", "north", "ada", "2")
    workspace.record_consensus_report(nearest_id, "three", "south", "ada", "1")
    suggested = workspace.agree_consensus(nearest_id)
    assert suggested["consensus"]["proposals"] == [
        _proposal("north", "nora"),
        _proposal("south", "mina"),
    ]

    finished = _in_progress(workspace, "Nothing left")
    finished_id = finished["id"]
    workspace.name_consensus_point(finished_id, "ada", "1")
    workspace.name_consensus_node(finished_id, "north")
    workspace.name_consensus_node(finished_id, "south")
    workspace.record_consensus_report(finished_id, "one", "north", "ada", "2")
    workspace.record_consensus_report(finished_id, "two", "south", "ada", "1")
    left = workspace.agree_consensus(finished_id)
    assert isinstance(left, Refusal)
    assert left.message == "No point is left to try."

    added = _in_progress(workspace, "New point")
    added_id = added["id"]
    workspace.name_consensus_point(added_id, "ada", "1")
    workspace.name_consensus_point(added_id, "grace", "2")
    workspace.name_consensus_point(added_id, "mina", "1")
    workspace.name_consensus_node(added_id, "north")
    workspace.record_consensus_report(added_id, "one", "north", "ada", "2")
    stored = workspace.agree_consensus(added_id)
    assert stored["consensus"]["choice"] == _choice("mina", "north", 1)
    workspace.name_consensus_point(added_id, "ada", "2")
    assert workspace.get_task(added_id)["consensus"]["choice"] == _choice("mina", "north", 1)
    workspace.name_consensus_point(added_id, "nora", "2")
    assert workspace.get_task(added_id)["consensus"]["choice"] is None

    joined = _in_progress(workspace, "New node")
    joined_id = joined["id"]
    workspace.name_consensus_point(joined_id, "ada", "1")
    workspace.name_consensus_point(joined_id, "mina", "1")
    workspace.name_consensus_node(joined_id, "north")
    workspace.record_consensus_report(joined_id, "one", "north", "ada", "2")
    workspace.agree_consensus(joined_id)
    workspace.name_consensus_node(joined_id, "north")
    assert workspace.get_task(joined_id)["consensus"]["choice"] == _choice("mina", "north", 1)
    workspace.name_consensus_node(joined_id, "south")
    assert workspace.get_task(joined_id)["consensus"]["choice"] is None

    refused = _in_progress(workspace, "Refused report")
    refused_id = refused["id"]
    workspace.name_consensus_point(refused_id, "ada", "1")
    workspace.name_consensus_point(refused_id, "mina", "1")
    workspace.name_consensus_node(refused_id, "north")
    workspace.name_consensus_node(refused_id, "south")
    workspace.record_consensus_report(refused_id, "one", "north", "ada", "2")
    workspace.record_consensus_report(refused_id, "two", "south", "ada", "1")
    workspace.agree_consensus(refused_id)
    duplicate = workspace.record_consensus_report(refused_id, "three", "north", "ada", "1")
    assert isinstance(duplicate, Refusal)
    assert duplicate.message == "That node already reported this point."
    assert workspace.get_task(refused_id)["consensus"]["choice"] == _choice("mina", "north", 2)

    empty = _in_progress(workspace, "Empty consensus")
    empty_id = empty["id"]
    missing = workspace.agree_consensus(empty_id)
    assert isinstance(missing, Refusal)
    assert missing.message == "Name a point first."
    workspace.name_consensus_point(empty_id, "ada", "1")
    no_node = workspace.agree_consensus(empty_id)
    assert isinstance(no_node, Refusal)
    assert no_node.message == "Name a node first."
    workspace.name_consensus_node(empty_id, "north")
    waiting = workspace.agree_consensus(empty_id)
    assert isinstance(waiting, Refusal)
    assert waiting.message == "Record a report first."

    draft = workspace.create_task("Draft")
    draft_refused = workspace.agree_consensus(draft["id"])
    assert isinstance(draft_refused, Refusal)
    assert draft_refused.message == "The task must be In Progress."

    fresh = _in_progress(workspace, "Rollback")
    fresh_id = fresh["id"]
    workspace.name_consensus_point(fresh_id, "ada", "1")
    workspace.name_consensus_point(fresh_id, "grace", "2")
    workspace.name_consensus_point(fresh_id, "mina", "1")
    workspace.name_consensus_node(fresh_id, "north")
    workspace.name_consensus_node(fresh_id, "south")
    workspace.record_consensus_report(fresh_id, "one", "north", "ada", "2")
    workspace.record_consensus_report(fresh_id, "two", "south", "ada", "1")
    assert workspace.agree_consensus(fresh_id)["consensus"]["choice"] == _choice("mina", "north", 2)

    def rolled(connection):
        consensus.record_report(
            connection, fresh_id, "three", "north", "grace", "1", "2026-10-22T00:00:00Z"
        )
        consensus.agree(connection, fresh_id, "2026-10-22T00:00:00Z")
        return bad_request("stop")

    assert isinstance(call_in_transaction(workspace.connection, rolled), Refusal)
    restored = workspace.get_task(fresh_id)
    assert len(restored["consensus"]["reports"]) == 2
    assert restored["consensus"]["proposals"] == [
        _proposal("north", "mina"),
        _proposal("south", "mina"),
    ]
    assert restored["consensus"]["choice"] == _choice("mina", "north", 2)
