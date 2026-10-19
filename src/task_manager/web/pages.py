"""Server-rendered list and task detail. Forms call the same commands as the API."""

import secrets

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
        {
            "tasks": _workspace(request).list_tasks(),
            "order": _workspace(request).execution_order(),
            "message": message,
        },
    )


def _render_detail(request: Request, task_id: int, message: str | None = None):
    detail = _workspace(request).get_task(task_id)
    if isinstance(detail, Refusal):
        return HTMLResponse(detail.message, status_code=detail.code)
    return templates.TemplateResponse(
        request,
        "detail.html",
        {"task": detail, "message": message, "advance_name": secrets.token_hex(8)},
    )


def _after(request: Request, task_id: int, result, fallback_id: int | None = None):
    if isinstance(result, Refusal):
        target = fallback_id if fallback_id is not None else task_id
        return _render_detail(request, target, result.message)
    return RedirectResponse(f"/tasks/{task_id}", status_code=303)


@router.get("/")
def list_page(request: Request):
    return _render_list(request)


@router.get("/instructions")
def instructions_page(request: Request):
    return _render_instructions(request)


@router.post("/instructions/model")
def save_model_page(
    request: Request,
    name: str = Form(""),
    base_url: str = Form(""),
    api_key: str = Form(""),
):
    result = _workspace(request).configure_model(name, base_url, api_key)
    if isinstance(result, Refusal):
        return _render_instructions(request, result.message)
    return RedirectResponse("/instructions", status_code=303)


@router.post("/instructions")
def start_instruction_page(
    request: Request,
    title: str = Form(""),
    goal: str = Form(""),
    criterion: str = Form(""),
    project: str = Form(""),
    read_path: str = Form(""),
    file: str = Form(""),
    change_class: str = Form("", alias="class"),
    what_changed: str = Form(""),
):
    result = _workspace(request).start_instruction(
        title,
        goal,
        criterion,
        project,
        read_path,
        file,
        change_class,
        what_changed,
    )
    if isinstance(result, Refusal):
        return _render_instructions(
            request,
            result.message,
            {
                "title": title,
                "goal": goal,
                "criterion": criterion,
                "project": project,
                "read_path": read_path,
                "file": file,
                "class": change_class,
                "what": what_changed,
            },
        )
    return RedirectResponse(f"/tasks/{result['id']}", status_code=303)


def _render_instructions(request: Request, message: str | None = None, form: dict | None = None):
    return templates.TemplateResponse(
        request,
        "instructions.html",
        {
            "model": _workspace(request).model_settings(),
            "message": message,
            "form": form or {},
        },
    )


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


@router.post("/tasks/{task_id}/prerequisites")
def add_prerequisite(request: Request, task_id: int, prerequisite_id: str = Form("")):
    return _after(
        request,
        task_id,
        _workspace(request).add_prerequisite(task_id, _form_int(prerequisite_id)),
    )


@router.post("/tasks/{task_id}/prerequisites/{prerequisite_id}/remove")
def remove_prerequisite(request: Request, task_id: int, prerequisite_id: int):
    return _after(
        request,
        task_id,
        _workspace(request).remove_prerequisite(task_id, prerequisite_id),
    )


@router.post("/tasks/{task_id}/workflow-steps")
def add_workflow_step(
    request: Request,
    task_id: int,
    title: str = Form(""),
    action: str = Form(""),
    project: str = Form(""),
    path: str = Form(""),
    what_changed: str = Form(""),
    change_class: str = Form("", alias="class"),
):
    return _after(
        request,
        task_id,
        _workspace(request).add_workflow_step(
            task_id,
            title,
            action,
            project,
            path,
            what_changed,
            change_class or None,
        ),
    )


@router.post("/tasks/{task_id}/workflow-steps/{step_id}/remove")
def remove_workflow_step(request: Request, task_id: int, step_id: int):
    return _after(
        request,
        task_id,
        _workspace(request).remove_workflow_step(task_id, step_id),
    )


@router.post("/tasks/{task_id}/workflow/advance")
def advance_workflow(request: Request, task_id: int, name: str = Form("")):
    return _after(request, task_id, _workspace(request).advance_workflow(task_id, name))


@router.post("/tasks/{task_id}/workflow/recover")
def recover_workflow(request: Request, task_id: int):
    return _after(request, task_id, _workspace(request).recover_workflow(task_id))


@router.post("/tasks/{task_id}/workflow/revise")
def revise_workflow(request: Request, task_id: int):
    return _after(request, task_id, _workspace(request).revise_workflow(task_id))


@router.post("/tasks/{task_id}/workflow/migrate")
def migrate_workflow(request: Request, task_id: int, reason: str = Form("")):
    return _after(request, task_id, _workspace(request).migrate_workflow(task_id, reason))


@router.post("/tasks/{task_id}/workflow/replay-execution")
def replay_workflow_execution(request: Request, task_id: int):
    return _after(request, task_id, _workspace(request).replay_workflow_execution(task_id))


@router.post("/tasks/{task_id}/workflow/replay-isolated")
def replay_isolated_effects(request: Request, task_id: int):
    return _after(request, task_id, _workspace(request).replay_isolated_effects(task_id))


@router.post("/tasks/{task_id}/workflow/outbox")
def deliver_outbox(request: Request, task_id: int, name: str = Form("")):
    return _after(request, task_id, _workspace(request).deliver_outbox(task_id, name))


@router.post("/tasks/{task_id}/workflow/checkpoints")
def take_checkpoint(request: Request, task_id: int, name: str = Form("")):
    return _after(request, task_id, _workspace(request).take_checkpoint(task_id, name))


@router.post("/tasks/{task_id}/workflow/checkpoints/{checkpoint_id}/restore")
def restore_checkpoint(request: Request, task_id: int, checkpoint_id: int):
    return _after(
        request, task_id, _workspace(request).restore_checkpoint(task_id, checkpoint_id)
    )


@router.post("/tasks/{task_id}/workflow/outbox/reject")
def reject_outbox(
    request: Request, task_id: int, name: str = Form(""), reason: str = Form("")
):
    return _after(
        request, task_id, _workspace(request).reject_outbox(task_id, name, reason)
    )


@router.post("/tasks/{task_id}/workflow/compensate")
def compensate_workflow(request: Request, task_id: int, reason: str = Form("")):
    return _after(request, task_id, _workspace(request).compensate_workflow(task_id, reason))


@router.post("/tasks/{task_id}/workflow/compensations/{compensation_id}/approve")
def approve_compensation(
    request: Request, task_id: int, compensation_id: int, evidence: str = Form("")
):
    return _after(
        request,
        task_id,
        _workspace(request).approve_compensation(task_id, compensation_id, evidence),
    )


@router.post("/tasks/{task_id}/workflow/compensations/{compensation_id}/decline")
def decline_compensation(
    request: Request, task_id: int, compensation_id: int, reason: str = Form("")
):
    return _after(
        request,
        task_id,
        _workspace(request).decline_compensation(task_id, compensation_id, reason),
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
    execution: str = Form(""),
):
    return _after(
        request,
        task_id,
        _workspace(request).record_file_read(task_id, project, file_path, execution=execution),
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
    execution: str = Form(""),
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
            execution,
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
