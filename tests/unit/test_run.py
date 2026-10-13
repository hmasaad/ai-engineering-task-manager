import subprocess

from task_manager.domain.results import Refusal
from task_manager.workspace import Workspace

LABEL = "tests/test_label.py::test_label"


def _started(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _write_label(root):
    tests = root / "billing" / "tests"
    tests.mkdir(parents=True)
    (tests / "test_label.py").write_text(
        "from pathlib import Path\n\n"
        "def test_label():\n"
        "    path = Path(__file__).with_name('ran.txt')\n"
        "    path.write_text((path.read_text() if path.exists() else '') + 'x')\n",
        encoding="utf-8",
    )
    (tests / "test_bad.py").write_text(
        "def test_bad():\n    assert False\n",
        encoding="utf-8",
    )


def _open(tmp_path, clock):
    root = tmp_path / "projects"
    _write_label(root)
    store = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    return store, root


def _ran(root):
    return root / "billing" / "tests" / "ran.txt"


def test_an_ordinary_test_runs_once(tmp_path, clock):
    workspace, root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        recorded = workspace.record_test(
            started["id"], " billing ", "ordinary", " Run the label test ", False, f" {LABEL} "
        )
        change = recorded["implementation_changes"][0]
        assert recorded["status"] == "In Progress"
        assert change["class"] == "ordinary"
        assert change["outcome"] == "Carried out"
        assert change["assistant_name"] == "Guide"
        assert change["test"]["path"] == LABEL
        assert change["test"]["result"] == "Passed"
        assert "passed" in change["test"]["output"]
        assert _ran(root).read_text() == "x"
        assert workspace.list_requirements() == []
        again = workspace.get_task(started["id"])
        assert len(again["implementation_changes"]) == 1
        assert again["implementation_changes"][0]["test"]["result"] == "Passed"
        assert _ran(root).read_text() == "x"
    finally:
        workspace.close()


def test_a_failed_test_is_stored_and_the_task_stays_in_progress(tmp_path, clock):
    workspace, root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        recorded = workspace.record_test(
            started["id"], "billing", "ordinary", "Run the failing test", False, "tests/test_bad.py::test_bad"
        )
        change = recorded["implementation_changes"][0]
        assert recorded["status"] == "In Progress"
        assert change["outcome"] == "Carried out"
        assert change["test"]["result"] == "Failed"
        assert "assert False" in change["test"]["output"]
    finally:
        workspace.close()


def test_a_blank_file_missing_and_outside_test_are_refused(tmp_path, clock):
    workspace, root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        blank = workspace.record_test(started["id"], "billing", "ordinary", "Run it", False, "  ")
        assert isinstance(blank, Refusal)
        assert blank.message == "Name the test this change runs."
        whole_file = workspace.record_test(
            started["id"], "billing", "ordinary", "Run it", False, "tests/test_label.py"
        )
        assert whole_file.message == "Name one test in a file."
        missing = workspace.record_test(
            started["id"], "billing", "ordinary", "Run it", False, "tests/test_missing.py::test_label"
        )
        assert missing.message == "The test must already exist."
        outside = workspace.record_test(
            started["id"], "billing", "ordinary", "Run it", False, "../outside.py::test_label"
        )
        assert outside.message == "The test must stay inside the named project."
        assert workspace.get_task(started["id"])["implementation_changes"] == []
        assert not _ran(root).exists()
    finally:
        workspace.close()


def test_a_consequential_test_waits_until_approval(tmp_path, clock):
    workspace, root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        waiting = workspace.record_test(
            started["id"], "billing", "consequential", "Run the label test", False, LABEL
        )
        change = waiting["implementation_changes"][0]
        assert change["class"] == "consequential"
        assert change["outcome"] == "Awaiting approval"
        assert change["test"]["result"] is None
        assert not _ran(root).exists()
        refused = workspace.approve_change(started["id"], change["id"], "Seen", actor="assistant")
        assert refused.message == "The assistant cannot approve a change."
        assert not _ran(root).exists()
        approved = workspace.approve_change(started["id"], change["id"], "The test is still the named file")
        carried = approved["implementation_changes"][0]
        assert carried["outcome"] == "Carried out"
        assert carried["test"]["result"] == "Passed"
        assert _ran(root).read_text() == "x"
        again = workspace.get_task(started["id"])
        assert _ran(root).read_text() == "x"
        assert again["implementation_changes"][0]["test"]["result"] == "Passed"
    finally:
        workspace.close()


def test_decline_and_a_missing_file_do_not_run(tmp_path, clock):
    workspace, root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        waiting = workspace.record_test(
            started["id"], "billing", "consequential", "Run the label test", False, LABEL
        )
        change_id = waiting["implementation_changes"][0]["id"]
        declined = workspace.mark_change_not_carried_out(started["id"], change_id, "Not this test")
        assert declined["implementation_changes"][0]["outcome"] == "Not carried out"
        assert not _ran(root).exists()
        replacement = workspace.record_test(
            started["id"], "billing", "consequential", "Run it later", False, LABEL
        )
        second = replacement["implementation_changes"][1]["id"]
        (root / "billing" / "tests" / "test_label.py").unlink()
        mismatched = workspace.approve_change(started["id"], second, "The file should still be there")
        assert isinstance(mismatched, Refusal)
        assert mismatched.message == "The test no longer matches the path this change was proposed against."
        assert not _ran(root).exists()
        still = workspace.get_task(started["id"])["implementation_changes"][1]
        assert still["outcome"] == "Awaiting approval"
    finally:
        workspace.close()


def test_a_stopped_ordinary_request_does_not_run(tmp_path, clock):
    workspace, root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        waiting = workspace.record_test(
            started["id"], "billing", "ordinary", "Run the label test", True, LABEL
        )
        change = waiting["implementation_changes"][0]
        assert change["class"] == "consequential"
        assert change["stopped"] is True
        assert change["outcome"] == "Awaiting approval"
        assert change["test"]["result"] is None
        assert not _ran(root).exists()
    finally:
        workspace.close()


def test_a_test_that_cannot_start_stores_nothing(tmp_path, clock, monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("pytest is not available")

    monkeypatch.setattr(subprocess, "run", fail)
    workspace, root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        refused = workspace.record_test(
            started["id"], "billing", "ordinary", "Run the label test", False, LABEL
        )
        assert isinstance(refused, Refusal)
        assert refused.message == "The test could not be run."
        assert workspace.get_task(started["id"])["implementation_changes"] == []
        assert not _ran(root).exists()
    finally:
        workspace.close()


def test_a_test_that_does_not_finish_is_stored_as_failed(tmp_path, clock, monkeypatch):
    def stall(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args, timeout=30, output="still running", stderr="")

    monkeypatch.setattr(subprocess, "run", stall)
    workspace, _root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        recorded = workspace.record_test(
            started["id"], "billing", "ordinary", "Run the label test", False, LABEL
        )
        change = recorded["implementation_changes"][0]
        assert change["outcome"] == "Carried out"
        assert change["test"]["result"] == "Failed"
        assert "The test did not finish." in change["test"]["output"]
    finally:
        workspace.close()
