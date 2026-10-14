import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class _Reply(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        payload = json.dumps(
            {"choices": [{"message": {"content": "Mark Attendance\n"}}]}
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        return


def test_the_page_saves_the_model_and_starts_work(client, tmp_path):
    home = client.get("/")
    assert 'href="/instructions"' in home.text
    page = client.get("/instructions")
    assert page.status_code == 200
    for field_id in (
        "model-name",
        "model-address",
        "model-key",
        "instruction-title",
        "instruction-goal",
        "instruction-criterion",
        "instruction-project",
        "instruction-read",
        "instruction-file",
        "instruction-class",
        "instruction-what",
    ):
        assert f'id="{field_id}"' in page.text
    assert 'id="model-text"' not in page.text
    assert "Model text" not in page.text
    assert "Save model" in page.text
    assert "Start work" in page.text

    empty = client.get("/api/model")
    assert empty.json() == {"name": None, "base_url": None, "api_key": None}
    blank = client.post("/api/model", json={"name": " ", "base_url": "http://127.0.0.1:1/v1"})
    assert blank.status_code == 400
    assert blank.json()["message"] == "Choose the model this change uses."
    bad_address = client.post("/api/model", json={"name": "Guide", "base_url": " "})
    assert bad_address.status_code == 400
    assert bad_address.json()["message"] == "Name the model service."

    server = ThreadingHTTPServer(("127.0.0.1", 0), _Reply)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    address = f"http://127.0.0.1:{server.server_address[1]}/v1"
    try:
        saved = client.post(
            "/api/model",
            json={"name": "Guide", "base_url": address, "text": "Export"},
        )
        assert saved.status_code == 200
        assert saved.json() == {"name": "Guide", "base_url": address, "api_key": None}

        project = tmp_path / "demo"
        project.mkdir()
        (project / "note.txt").write_text("hello\n", encoding="utf-8")
        missing = client.post(
            "/api/instructions",
            json={
                "title": "Record the note",
                "goal": "Take the record",
                "criterion": "The note is stored",
                "project": str(project),
                "read_path": "missing.txt",
                "file": "out.txt",
                "class": "ordinary",
                "what_changed": "Write the export",
            },
        )
        assert missing.status_code == 400
        assert missing.json()["message"] == "The file must already exist."
        assert client.get("/api/tasks").json() == []

        started = client.post(
            "/api/instructions",
            json={
                "title": "Record the note",
                "goal": "Take the record",
                "criterion": "The note is stored",
                "project": str(project),
                "read_path": "note.txt",
                "file": "out.txt",
                "class": "ordinary",
                "what_changed": "Change the heading to Mark Attendance",
            },
        )
        assert started.status_code == 200
        body = started.json()
        assert body["status"] == "In Progress"
        assert (project / "out.txt").read_text(encoding="utf-8") == "Mark Attendance\n"
        assert isinstance(client.get("/api/tasks").json(), list)

        shown = client.get("/instructions")
        assert 'value="Guide"' in shown.text
        assert address in shown.text
        task_page = client.get(f"/tasks/{body['id']}")
        assert "Mark Attendance" in task_page.text
        assert "note.txt" in task_page.text
    finally:
        server.shutdown()
