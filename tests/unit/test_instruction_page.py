import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from task_manager.domain.results import Refusal
from task_manager.workspace import Workspace


def _project(tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    return project


class _Reply(BaseHTTPRequestHandler):
    body = "Mark Attendance\n"

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        type(self).last = json.loads(raw.decode("utf-8"))
        type(self).authorization = self.headers.get("Authorization")
        payload = json.dumps(
            {"choices": [{"message": {"content": type(self).body}}]}
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        return


def _serve(body: str):
    handler = type("Reply", (_Reply,), {"body": body, "last": None})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    address = f"http://127.0.0.1:{server.server_address[1]}/v1"
    return server, handler, address


def test_a_saved_model_is_shown_again(workspace, tmp_path, clock):
    assert workspace.model_settings() == {"name": None, "base_url": None, "api_key": None}
    saved = workspace.configure_model("  Guide  ", " http://127.0.0.1:11434/v1 ", " secret ")
    assert saved == {
        "name": "Guide",
        "base_url": "http://127.0.0.1:11434/v1",
        "api_key": "secret",
    }
    opened = Workspace(tmp_path / "workspace.db", clock, "Ada")
    try:
        assert opened.model_settings() == saved
    finally:
        opened.close()
    assert workspace.configure_model(" ", "http://127.0.0.1:1/v1").message == (
        "Choose the model this change uses."
    )
    assert workspace.configure_model("Guide", "  ").message == "Name the model service."
    assert workspace.configure_model("Guide", "ftp://127.0.0.1/v1").message == (
        "Name the model service."
    )
    assert workspace.model_settings() == saved
    without_key = workspace.configure_model("Guide", "http://127.0.0.1:11434/v1", " ")
    assert without_key["api_key"] is None


def test_start_writes_a_new_file_from_the_model(workspace, tmp_path):
    project = _project(tmp_path)
    server, handler, address = _serve("```dart\nMark Attendance\n```")
    try:
        workspace.configure_model("Guide", address)
        started = workspace.start_instruction(
            "Record the note",
            "Take the record",
            "The note is stored",
            str(project),
            "note.txt",
            "out.txt",
            "ordinary",
            "Change the heading to Mark Attendance",
        )
    finally:
        server.shutdown()
    assert started["status"] == "In Progress"
    assert (project / "out.txt").read_text(encoding="utf-8") == "Mark Attendance\n"
    assert len(started["file_reads"]) == 1
    change = started["implementation_changes"][0]
    assert change["model"]["output"] == "Mark Attendance\n"
    assert change["outcome"] == "Carried out"
    assert len(workspace.model.prompts) == 1
    prompt = workspace.model.prompts[0]
    assert "hello\n" in prompt
    assert "Change the heading to Mark Attendance" in prompt
    assert handler.last["messages"][1]["content"] == prompt
    assert handler.authorization is None


def test_an_existing_file_waits_for_approval(workspace, tmp_path):
    project = _project(tmp_path)
    server, handler, address = _serve("Mark Attendance\n")
    try:
        workspace.configure_model("Guide", address, "secret")
        started = workspace.start_instruction(
            "Revise the note",
            "Take the record",
            "The note is stored",
            str(project),
            "note.txt",
            "note.txt",
            "ordinary",
            "Change the heading to Mark Attendance",
        )
        assert started["status"] == "In Progress"
        assert (project / "note.txt").read_text(encoding="utf-8") == "hello\n"
        change = started["implementation_changes"][0]
        assert change["outcome"] == "Awaiting approval"
        assert change["model"]["output"] == "Mark Attendance\n"
        assert "secret" not in workspace.model.prompts[0]
        assert handler.authorization == "Bearer secret"
        assert len(workspace.model.prompts) == 1
        approved = workspace.approve_change(started["id"], change["id"], "The heading matches.")
    finally:
        server.shutdown()
    assert (project / "note.txt").read_text(encoding="utf-8") == "Mark Attendance\n"
    assert approved["implementation_changes"][0]["outcome"] == "Carried out"
    assert len(workspace.model.prompts) == 1


def test_a_missing_file_stores_nothing(workspace, tmp_path):
    project = _project(tmp_path)
    server, _, address = _serve("Mark Attendance\n")
    try:
        workspace.configure_model("Guide", address)
        refused = workspace.start_instruction(
            "Record the note",
            "Take the record",
            "The note is stored",
            str(project),
            "missing.txt",
            "out.txt",
            "ordinary",
            "Write the export",
        )
    finally:
        server.shutdown()
    assert isinstance(refused, Refusal)
    assert refused.message == "The file must already exist."
    assert workspace.list_tasks() == []
    assert not (project / "out.txt").exists()
    assert workspace.model.prompts == []


def test_an_unreachable_service_stores_nothing(workspace, tmp_path):
    project = _project(tmp_path)
    closed = ThreadingHTTPServer(("127.0.0.1", 0), _Reply)
    address = f"http://127.0.0.1:{closed.server_address[1]}/v1"
    closed.server_close()
    workspace.configure_model("Guide", address)
    refused = workspace.start_instruction(
        "Record the note",
        "Take the record",
        "The note is stored",
        str(project),
        "note.txt",
        "out.txt",
        "ordinary",
        "Write the export",
    )
    assert isinstance(refused, Refusal)
    assert refused.message == "The model service could not be reached."
    assert workspace.list_tasks() == []
    assert not (project / "out.txt").exists()


def test_an_empty_reply_stores_nothing(workspace, tmp_path):
    project = _project(tmp_path)
    server, _, address = _serve("   ")
    try:
        workspace.configure_model("Guide", address)
        refused = workspace.start_instruction(
            "Record the note",
            "Take the record",
            "The note is stored",
            str(project),
            "note.txt",
            "out.txt",
            "ordinary",
            "Write the export",
        )
    finally:
        server.shutdown()
    assert isinstance(refused, Refusal)
    assert refused.message == "The model did not return file text."
    assert workspace.list_tasks() == []
    assert not (project / "out.txt").exists()


def test_starting_without_a_model_stores_one_task_only_after_a_model_exists(workspace, tmp_path):
    project = _project(tmp_path)
    server, _, address = _serve("Mark Attendance\n")
    try:
        workspace.configure_model("Guide", address)
        unnamed = workspace.start_instruction(
            "Record the note",
            "Take the record",
            "The note is stored",
            str(project),
            "note.txt",
            "out.txt",
            "ordinary",
            "Write the export",
        )
        workspace.model = None
        refused_model = workspace.start_instruction(
            "Record the note",
            "Take the record",
            "The note is stored",
            str(project),
            "note.txt",
            "out.txt",
            "ordinary",
            "Write the export",
        )
    finally:
        server.shutdown()
    assert unnamed["status"] == "In Progress"
    assert refused_model.message == "Choose the model this change uses."
    assert len(workspace.list_tasks()) == 1
