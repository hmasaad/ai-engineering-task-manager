from task_manager.domain.results import Refusal
from task_manager.model import ScriptedModel
from task_manager.workspace import Workspace


def _open(tmp_path, clock, model):
    root = tmp_path / "projects"
    notes = root / "billing" / "notes"
    notes.mkdir(parents=True)
    (notes / "label.txt").write_text("Export", encoding="utf-8")
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root, model)
    created = workspace.create_task("Add export")
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The file contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    started = workspace.transition(ready["id"], "start")
    read = workspace.record_file_read(started["id"], "billing", "notes/label.txt")
    return workspace, root, read


def test_ordinary_new_file_calls_the_model_once(tmp_path, clock):
    model = ScriptedModel("Guide-model", "From the model")
    workspace, root, started = _open(tmp_path, clock, model)
    try:
        read_id = started["file_reads"][0]["id"]
        recorded = workspace.record_model_file(
            started["id"],
            " billing ",
            "ordinary",
            " Propose the export label ",
            False,
            "notes/proposed.txt",
            read_id,
        )
        change = recorded["implementation_changes"][0]
        proposed = root / "billing" / "notes" / "proposed.txt"
        assert recorded["status"] == "In Progress"
        assert change["outcome"] == "Carried out"
        assert change["class"] == "ordinary"
        assert change["assistant_name"] == "Guide"
        assert change["file"]["was_new"] is True
        assert change["file"]["text"] == "From the model"
        assert change["model"]["name"] == "Guide-model"
        assert change["model"]["output"] == "From the model"
        assert change["model"]["file_read_id"] == read_id
        assert "Task: Add export" in change["model"]["input"]
        assert "Export" in change["model"]["input"]
        assert proposed.read_text(encoding="utf-8") == "From the model"
        assert len(model.prompts) == 1
        assert (root / "billing" / "notes" / "label.txt").read_text(encoding="utf-8") == "Export"
    finally:
        workspace.close()


def test_refusals_do_not_call_the_model(tmp_path, clock):
    model = ScriptedModel("Guide-model", "From the model")
    workspace, root, started = _open(tmp_path, clock, model)
    try:
        read_id = started["file_reads"][0]["id"]
        blank = workspace.record_model_file(
            started["id"], "   ", "ordinary", "Propose the export label", False, "notes/proposed.txt", read_id
        )
        assert isinstance(blank, Refusal)
        assert blank.message == "Name the project this change is for."
        missing_read = workspace.record_model_file(
            started["id"], "billing", "ordinary", "Propose the export label", False, "notes/proposed.txt", None
        )
        assert isinstance(missing_read, Refusal)
        assert missing_read.message == "Choose the file read this change uses."
        unknown = workspace.record_model_file(
            started["id"], "billing", "ordinary", "Propose the export label", False, "notes/proposed.txt", 9999
        )
        assert isinstance(unknown, Refusal)
        assert unknown.message == "File read not found."
        outside = workspace.record_model_file(
            started["id"], "billing", "ordinary", "Propose the export label", False, "../outside.txt", read_id
        )
        assert isinstance(outside, Refusal)
        assert outside.message == "The file must stay inside the named project."
        assert len(model.prompts) == 0
        assert workspace.get_task(started["id"])["implementation_changes"] == []
        assert not (root / "outside.txt").exists()
    finally:
        workspace.close()


def test_a_missing_model_and_a_failed_call_store_nothing(tmp_path, clock):
    workspace, root, started = _open(tmp_path, clock, None)
    try:
        read_id = started["file_reads"][0]["id"]
        missing_model = workspace.record_model_file(
            started["id"], "billing", "ordinary", "Propose the export label", False, "notes/proposed.txt", read_id
        )
        assert isinstance(missing_model, Refusal)
        assert missing_model.message == "Choose the model this change uses."

        class Broken:
            name = "Guide-model"

            def complete(self, prompt):
                raise RuntimeError("down")

        workspace.model = Broken()
        failed = workspace.record_model_file(
            started["id"], "billing", "ordinary", "Propose the export label", False, "notes/proposed.txt", read_id
        )
        assert isinstance(failed, Refusal)
        assert failed.message == "The model did not return file text."
        assert not (root / "billing" / "notes" / "proposed.txt").exists()
        assert workspace.get_task(started["id"])["implementation_changes"] == []
    finally:
        workspace.close()


def test_approval_writes_the_stored_text_without_another_call(tmp_path, clock):
    model = ScriptedModel("Guide-model", "Proposed")
    workspace, root, started = _open(tmp_path, clock, model)
    try:
        label = root / "billing" / "notes" / "label.txt"
        label.write_text("Old", encoding="utf-8")
        read_id = started["file_reads"][0]["id"]
        waiting = workspace.record_model_file(
            started["id"], "billing", "ordinary", "Replace the label", False, "notes/label.txt", read_id
        )
        assert label.read_text(encoding="utf-8") == "Old"
        assert len(model.prompts) == 1
        assert "Export" in model.prompts[0]
        change_id = waiting["implementation_changes"][0]["id"]
        approved = workspace.approve_change(started["id"], change_id, "The page shows the model text")
        assert approved["implementation_changes"][0]["outcome"] == "Carried out"
        assert approved["implementation_changes"][0]["approval"]["engineer_name"] == "Ada"
        assert label.read_text(encoding="utf-8") == "Proposed"
        assert len(model.prompts) == 1
        assistant = workspace.approve_change(started["id"], change_id, "Again", actor="assistant")
        assert isinstance(assistant, Refusal)
        assert assistant.message == "The assistant cannot approve a change."
        assert len(model.prompts) == 1
    finally:
        workspace.close()
