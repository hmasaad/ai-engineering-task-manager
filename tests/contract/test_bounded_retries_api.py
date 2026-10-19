from task_manager.clock import format_time
from fastapi.testclient import TestClient

import pytest

from task_manager.web.app import create_app
from task_manager.workspace import Workspace


@pytest.fixture
def retry_client(tmp_path, clock):
    root = tmp_path / "projects"
    project = root / "billing"
    project.mkdir(parents=True)
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    application = create_app(workspace)
    with TestClient(application) as test_client:
        yield test_client, clock
    workspace.close()


def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_shows_one_attempt(retry_client):
    client, clock = retry_client
    task_id = _in_progress(client)
    client.post(
        f"/api/tasks/{task_id}/workflow-steps",
        json={
            "title": "Read the note",
            "action": "read",
            "project": "billing",
            "path": "note.txt",
        },
    )
    client.post(f"/api/tasks/{task_id}/workflow/advance", json={})
    attempted = client.post(
        f"/api/tasks/{task_id}/workflow/outbox/retry",
        json={"name": "once"},
    )
    assert attempted.status_code == 200
    retry = attempted.json()["workflow"]["retries"][0]
    assert retry["attempt_count"] == 1
    shown = client.get(f"/tasks/{task_id}")
    assert 'id="workflow-retries"' in shown.text
    assert "Attempts 1" in shown.text
    assert retry["next_eligible_at"] in shown.text
    assert "Delivery did not succeed" in shown.text
    early = client.post(
        f"/api/tasks/{task_id}/workflow/outbox",
        json={"name": "ship"},
    )
    assert early.status_code == 409
    assert early.json()["message"] == "This delivery is not due yet."
    page = client.post(
        f"/tasks/{task_id}/workflow/outbox/retry",
        data={"name": "twice"},
        follow_redirects=True,
    )
    assert "This delivery is not due yet." in page.text
    assert client.get(f"/api/tasks/{task_id}").json()["workflow"]["retries"][0]["attempt_count"] == 1
    while format_time(clock.now()) < retry["next_eligible_at"]:
        pass
    delivered = client.post(
        f"/api/tasks/{task_id}/workflow/outbox",
        json={"name": "ship"},
    )
    assert delivered.status_code == 200
    assert delivered.json()["workflow"]["outbox"][0]["state"] == "Delivered"
    assert isinstance(client.get("/api/tasks").json(), list)
