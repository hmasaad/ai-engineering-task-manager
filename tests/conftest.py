from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from task_manager.clock import ScriptedClock
from task_manager.web.app import create_app
from task_manager.workspace import Workspace


@pytest.fixture
def clock():
    return ScriptedClock(start=datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc))


@pytest.fixture
def workspace(tmp_path, clock):
    store = Workspace(tmp_path / "workspace.db", clock, "Ada")
    yield store
    store.close()


@pytest.fixture
def client(workspace):
    application = create_app(workspace)
    with TestClient(application) as test_client:
        yield test_client
