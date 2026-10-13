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
    method: str = Form(""),
    run_identifier: str = Form(""),
):
    return _after(
        request,
        task_id,
        _workspace(request).verify_criterion(
            task_id, criterion_id, observation, pass_result, method, run_identifier
        ),
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


@router.post("/tasks/{task_id}/model-files")
def record_model_file(
    request: Request,
    task_id: int,
    project: str = Form(""),
    what_changed: str = Form(""),
    change_class: str = Form("", alias="class"),
    stopped: str = Form(""),
    file_path: str = Form("", alias="file"),
    file_read_id: str = Form(""),
):
    chosen = int(file_read_id) if file_read_id.strip().isdigit() else None
    return _after(
        request,
        task_id,
        _workspace(request).record_model_file(
            task_id,
            project,
            change_class or None,
            what_changed,
            stopped == "true",
            file_path,
            chosen,
        ),
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


@router.post("/tasks/{task_id}/folders")
def record_folder(
    request: Request,
    task_id: int,
    project: str = Form(""),
    what_changed: str = Form(""),
    change_class: str = Form("", alias="class"),
    stopped: str = Form(""),
    folder_path: str = Form("", alias="folder"),
):
    return _after(
        request,
        task_id,
        _workspace(request).record_folder(
            task_id,
            project,
            change_class or None,
            what_changed,
            stopped == "true",
            folder_path,
        ),
    )


@router.post("/tasks/{task_id}/test-runs")
def record_test(
    request: Request,
    task_id: int,
    project: str = Form(""),
    what_changed: str = Form(""),
    change_class: str = Form("", alias="class"),
    stopped: str = Form(""),
    test_path: str = Form("", alias="test"),
):
    return _after(
        request,
        task_id,
        _workspace(request).record_test(
            task_id,
            project,
            change_class or None,
            what_changed,
            stopped == "true",
            test_path,
        ),
    )


@router.post("/tasks/{task_id}/pull-requests")
def record_pull_request(
    request: Request,
    task_id: int,
    project: str = Form(""),
    what_changed: str = Form(""),
    change_class: str = Form("", alias="class"),
    stopped: str = Form(""),
    branch: str = Form(""),
):
    return _after(
        request,
        task_id,
        _workspace(request).record_pull_request(
            task_id,
            project,
            change_class or None,
            what_changed,
            stopped == "true",
            branch,
        ),
    )


@router.post("/tasks/{task_id}/branches")
def record_branch(
    request: Request,
    task_id: int,
    project: str = Form(""),
    what_changed: str = Form(""),
    change_class: str = Form("", alias="class"),
    stopped: str = Form(""),
    branch_name: str = Form("", alias="branch"),
):
    return _after(
        request,
        task_id,
        _workspace(request).record_branch(
            task_id,
            project,
            change_class or None,
            what_changed,
            stopped == "true",
            branch_name,
        ),
    )


@router.post("/tasks/{task_id}/commits")
def record_commit(
    request: Request,
    task_id: int,
    project: str = Form(""),
    what_changed: str = Form(""),
    change_class: str = Form("", alias="class"),
    stopped: str = Form(""),
    file_path: str = Form("", alias="file"),
):
    return _after(
        request,
        task_id,
        _workspace(request).record_commit(
            task_id,
            project,
            change_class or None,
            what_changed,
            stopped == "true",
            file_path,
        ),
    )


@router.post("/tasks/{task_id}/deletes")
def record_deletion(
    request: Request,
    task_id: int,
    project: str = Form(""),
    what_changed: str = Form(""),
    change_class: str = Form("", alias="class"),
    stopped: str = Form(""),
    file_path: str = Form("", alias="file"),
):
    return _after(
        request,
        task_id,
        _workspace(request).record_deletion(
            task_id,
            project,
            change_class or None,
            what_changed,
            stopped == "true",
            file_path,
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


@router.post("/tasks/{task_id}/assistant-checks")
def record_assistant_check(
    request: Request,
    task_id: int,
    change_id: str = Form(""),
    criterion_id: str = Form(""),
    evidence: str = Form(""),
    result: str = Form(""),
):
    chosen_change = int(change_id) if change_id.strip().isdigit() else None
    if chosen_change is None:
        return _after(
            request,
            task_id,
            Refusal(400, "The request is missing a required field or has the wrong shape."),
        )
    chosen = int(criterion_id) if criterion_id.strip().isdigit() else None
    return _after(
        request,
        task_id,
        _workspace(request).record_assistant_check(
            task_id, chosen_change, chosen, evidence, result or None
        ),
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


def _form_int(value: str) -> int | None:
    return int(value) if value.strip().isdigit() else None


def _render_requirements(request: Request, message: str | None = None) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "requirements.html",
        {
            "requirements": _workspace(request).list_requirements(),
            "trace": _workspace(request).traceability(),
            "message": message,
        },
    )


def _render_requirement(request: Request, requirement_id: int, message: str | None = None):
    detail = _workspace(request).get_requirement(requirement_id)
    if isinstance(detail, Refusal):
        return HTMLResponse(detail.message, status_code=detail.code)
    return templates.TemplateResponse(
        request,
        "requirement.html",
        {"requirement": detail, "message": message},
    )


def _after_requirement(request: Request, requirement_id: int, result):
    if isinstance(result, Refusal):
        if result.message == "Requirement not found.":
            return HTMLResponse(result.message, status_code=result.code)
        return _render_requirement(request, requirement_id, result.message)
    return RedirectResponse(f"/requirements/{requirement_id}", status_code=303)


@router.get("/requirements")
def requirements_page(request: Request):
    return _render_requirements(request)


@router.post("/requirements")
def create_requirement(request: Request, statement: str = Form(""), kind: str = Form("")):
    result = _workspace(request).record_requirement(statement, kind or None)
    if isinstance(result, Refusal):
        return _render_requirements(request, result.message)
    return RedirectResponse(f"/requirements/{result['id']}", status_code=303)


@router.get("/requirements/{requirement_id}")
def requirement_page(request: Request, requirement_id: int):
    return _render_requirement(request, requirement_id)


@router.post("/requirements/{requirement_id}")
def save_requirement(
    request: Request,
    requirement_id: int,
    statement: str = Form(""),
    kind: str = Form(""),
):
    return _after_requirement(
        request,
        requirement_id,
        _workspace(request).change_requirement(requirement_id, statement, kind or None),
    )


@router.post("/requirements/{requirement_id}/tasks")
def link_task(request: Request, requirement_id: int, task_id: str = Form("")):
    return _after_requirement(
        request,
        requirement_id,
        _workspace(request).link_requirement_task(requirement_id, _form_int(task_id)),
    )


@router.post("/requirements/{requirement_id}/criteria")
def link_criterion_page(
    request: Request,
    requirement_id: int,
    task_id: str = Form(""),
    criterion_id: str = Form(""),
):
    return _after_requirement(
        request,
        requirement_id,
        _workspace(request).link_requirement_criterion(
            requirement_id, _form_int(task_id), _form_int(criterion_id)
        ),
    )


@router.post("/requirements/{requirement_id}/tasks/{task_id}/unlink")
def unlink_task_page(request: Request, requirement_id: int, task_id: int):
    return _after_requirement(
        request,
        requirement_id,
        _workspace(request).unlink_requirement_task(requirement_id, task_id),
    )


@router.post("/requirements/{requirement_id}/criteria/{criterion_id}/unlink")
def unlink_criterion_page(request: Request, requirement_id: int, criterion_id: int):
    return _after_requirement(
        request,
        requirement_id,
        _workspace(request).unlink_requirement_criterion(requirement_id, criterion_id),
    )


@router.post("/requirements/{requirement_id}/checks")
def name_check_page(request: Request, requirement_id: int, name: str = Form("")):
    return _after_requirement(
        request,
        requirement_id,
        _workspace(request).name_requirement_check(requirement_id, name),
    )


@router.post("/requirements/{requirement_id}/checks/{check_id}/remove")
def remove_check_page(request: Request, requirement_id: int, check_id: int):
    return _after_requirement(
        request,
        requirement_id,
        _workspace(request).remove_requirement_check(requirement_id, check_id),
    )


@router.post("/requirements/{requirement_id}/runs")
def record_run_page(
    request: Request,
    requirement_id: int,
    check: str = Form(""),
    result: str = Form(""),
    run_identifier: str = Form(""),
):
    return _after_requirement(
        request,
        requirement_id,
        _workspace(request).record_requirement_run(
            requirement_id, check, result or None, run_identifier
        ),
    )
