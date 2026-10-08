"""Server-rendered list and task detail. Forms call the same commands as the API."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from task_manager.domain.results import Refusal

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def _workspace(request: Request):
    return request.app.state.workspace


def _render_list(request: Request, message: str | None = None) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "list.html",
        {"tasks": _workspace(request).list_tasks(), "message": message},
    )


def _render_detail(request: Request, task_id: int, message: str | None = None):
    detail = _workspace(request).get_task(task_id)
    if isinstance(detail, Refusal):
        return HTMLResponse(detail.message, status_code=detail.code)
    return templates.TemplateResponse(
        request,
        "detail.html",
        {"task": detail, "message": message},
    )


def _after(request: Request, task_id: int, result, fallback_id: int | None = None):
    if isinstance(result, Refusal):
        target = fallback_id if fallback_id is not None else task_id
        return _render_detail(request, target, result.message)
    return RedirectResponse(f"/tasks/{task_id}", status_code=303)


@router.get("/")
def list_page(request: Request):
    return _render_list(request)


@router.post("/tasks")
def create_task(request: Request, title: str = Form("")):
    result = _workspace(request).create_task(title)
    if isinstance(result, Refusal):
        return _render_list(request, result.message)
    return RedirectResponse(f"/tasks/{result['id']}", status_code=303)


@router.get("/tasks/{task_id}")
def detail_page(request: Request, task_id: int):
    return _render_detail(request, task_id)


@router.post("/tasks/{task_id}/goal")
def set_goal(request: Request, task_id: int, goal: str = Form("")):
    return _after(request, task_id, _workspace(request).set_goal(task_id, goal))


@router.post("/tasks/{task_id}/criteria")
def add_criterion(request: Request, task_id: int, text: str = Form("")):
    return _after(request, task_id, _workspace(request).add_criterion(task_id, text))


@router.post("/tasks/{task_id}/criteria/{criterion_id}/edit")
def edit_criterion(request: Request, task_id: int, criterion_id: int, text: str = Form("")):
    return _after(
        request, task_id, _workspace(request).update_criterion(task_id, criterion_id, text)
    )


@router.post("/tasks/{task_id}/criteria/{criterion_id}/remove")
def remove_criterion(request: Request, task_id: int, criterion_id: int):
    return _after(request, task_id, _workspace(request).remove_criterion(task_id, criterion_id))


@router.post("/tasks/{task_id}/transition")
def transition(
    request: Request,
    task_id: int,
    action: str = Form(...),
    reason: str = Form(""),
):
    return _after(
        request,
        task_id,
        _workspace(request).transition(task_id, action, reason or None),
    )


@router.post("/tasks/{task_id}/criteria/{criterion_id}/verify")
def verify(
    request: Request,
    task_id: int,
    criterion_id: int,
    observation: str = Form(""),
    pass_result: str = Form(""),
):
    return _after(
        request,
        task_id,
        _workspace(request).verify_criterion(task_id, criterion_id, observation, pass_result),
    )


@router.post("/tasks/{task_id}/criteria/{criterion_id}/unverify")
def unverify(request: Request, task_id: int, criterion_id: int):
    return _after(
        request, task_id, _workspace(request).unverify_criterion(task_id, criterion_id)
    )


@router.post("/tasks/{task_id}/subtasks")
def add_subtask(request: Request, task_id: int, title: str = Form("")):
    result = _workspace(request).add_subtask(task_id, title)
    if isinstance(result, Refusal):
        return _render_detail(request, task_id, result.message)
    return RedirectResponse(f"/tasks/{task_id}", status_code=303)


@router.post("/tasks/{task_id}/implementation-changes")
def record_change(
    request: Request,
    task_id: int,
    what_changed: str = Form(""),
    change_class: str = Form("", alias="class"),
):
    return _after(
        request,
        task_id,
        _workspace(request).record_change(task_id, what_changed, change_class or None),
    )


@router.post("/tasks/{task_id}/file-reads")
def record_file_read(
    request: Request,
    task_id: int,
    project: str = Form(""),
    file_path: str = Form("", alias="file"),
):
    return _after(
        request,
        task_id,
        _workspace(request).record_file_read(task_id, project, file_path),
    )


@router.post("/tasks/{task_id}/assistant-changes")
def record_assistant_change(
    request: Request,
    task_id: int,
    project: str = Form(""),
    what_changed: str = Form(""),
    change_class: str = Form("", alias="class"),
    stopped: str = Form(""),
    file_path: str = Form("", alias="file"),
    file_text: str = Form(""),
):
    return _after(
        request,
        task_id,
        _workspace(request).record_assistant_change(
            task_id,
            project,
            change_class or None,
            what_changed,
            stopped == "true",
            file_path,
            file_text,
        ),
    )


@router.post("/tasks/{task_id}/implementation-changes/{change_id}/approve")
def approve_change(
    request: Request,
    task_id: int,
    change_id: int,
    evidence: str = Form(""),
):
    return _after(
        request,
        task_id,
        _workspace(request).approve_change(task_id, change_id, evidence),
    )


@router.post("/tasks/{task_id}/implementation-changes/{change_id}/not-carried-out")
def mark_not_carried_out(
    request: Request,
    task_id: int,
    change_id: int,
    reason: str = Form(""),
):
    return _after(
        request,
        task_id,
        _workspace(request).mark_change_not_carried_out(task_id, change_id, reason),
    )


@router.post("/tasks/{task_id}/implementation-changes/{change_id}/checks")
def record_check(
    request: Request,
    task_id: int,
    change_id: int,
    criterion_id: str = Form(""),
    evidence: str = Form(""),
    result: str = Form(""),
):
    chosen = int(criterion_id) if criterion_id.strip().isdigit() else None
    return _after(
        request,
        task_id,
        _workspace(request).record_check(task_id, change_id, chosen, evidence, result or None),
    )


@router.post("/tasks/{task_id}/decisions")
def add_decision(
    request: Request,
    task_id: int,
    statement: str = Form(""),
    rationale: str = Form(""),
    supersedes: list[int] = Form(default=[]),
):
    return _after(
        request,
        task_id,
        _workspace(request).add_decision(task_id, statement, rationale, supersedes),
    )


@router.post("/tasks/{task_id}/linked-decisions")
def add_linked_decision(
    request: Request,
    task_id: int,
    statement: str = Form(""),
    rationale: str = Form(""),
    check_id: str = Form(""),
    supersedes: list[int] = Form(default=[]),
):
    chosen = int(check_id) if check_id.strip().isdigit() else None
    return _after(
        request,
        task_id,
        _workspace(request).add_linked_decision(
            task_id, statement, rationale, chosen, supersedes
        ),
    )
