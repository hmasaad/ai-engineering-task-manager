"""JSON commands. The pages call the same workspace methods."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from task_manager.domain.results import Refusal

router = APIRouter(prefix="/api")


class CreateTask(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str


class PrerequisiteIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    prerequisite_id: int


class WorkflowStepIn(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    title: str
    action: str = ""
    project: str = ""
    path: str = ""
    what_changed: str = ""
    change_class: str | None = Field(default=None, alias="class")


class AdvanceIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str = ""


class MigrateIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    reason: str = ""


class ModelIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str = ""
    base_url: str = ""
    api_key: str = ""


class InstructionIn(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    title: str = ""
    goal: str = ""
    criterion: str = ""
    project: str = ""
    read_path: str = ""
    file: str = ""
    change_class: str | None = Field(default=None, alias="class")
    what_changed: str = ""


class GoalUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    goal: str


class CriterionText(BaseModel):
    model_config = ConfigDict(extra="ignore")
    text: str


class TransitionIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    action: str
    reason: str | None = None


class VerifyIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    observation: str
    pass_result: str
    method: str = ""
    run_identifier: str = ""


class SubtaskIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str


class DecisionIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    statement: str
    rationale: str
    supersedes: list[int] = Field(default_factory=list)


class LinkedDecisionIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    statement: str
    rationale: str
    check_id: int | None = None
    supersedes: list[int] = Field(default_factory=list)


class ImplementationChangeIn(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    what_changed: str = ""
    change_class: str | None = Field(default=None, alias="class")


class ApprovalIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    evidence: str = ""
    actor: str | None = None


class NotCarriedOutIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    reason: str = ""
    actor: str | None = None


class ModelFileIn(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    project: str
    what_changed: str
    change_class: str | None = Field(default=None, alias="class")
    stopped: bool = False
    file: str
    file_read_id: int | None = None


class FileReadIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project: str
    file: str


class AssistantChangeIn(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    project: str
    what_changed: str
    change_class: str | None = Field(default=None, alias="class")
    stopped: bool = False
    file: str | None = None
    file_text: str | None = None


class FolderIn(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    project: str
    what_changed: str
    change_class: str | None = Field(default=None, alias="class")
    stopped: bool = False
    folder: str = ""


class CreateBranchIn(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    project: str
    what_changed: str
    change_class: str | None = Field(default=None, alias="class")
    stopped: bool = False
    branch: str = ""


class PullRequestIn(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    project: str
    what_changed: str
    change_class: str | None = Field(default=None, alias="class")
    stopped: bool = False
    branch: str = ""


class CommitFileIn(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    project: str
    what_changed: str
    change_class: str | None = Field(default=None, alias="class")
    stopped: bool = False
    file: str = ""


class DeleteFileIn(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    project: str
    what_changed: str
    change_class: str | None = Field(default=None, alias="class")
    stopped: bool = False
    file: str = ""


class TestRunIn(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    project: str
    what_changed: str
    change_class: str | None = Field(default=None, alias="class")
    stopped: bool = False
    test: str = ""


class CheckIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    criterion_id: int | None = None
    evidence: str = ""
    result: str | None = None


class AssistantCheckIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    change_id: int
    criterion_id: int | None = None
    evidence: str = ""
    result: str | None = None


def _respond(result):
    if isinstance(result, Refusal):
        return JSONResponse(status_code=result.code, content=result.body)
    return result


@router.get("/execution-order")
def execution_order(request: Request):
    return request.app.state.workspace.execution_order()


@router.get("/model")
def get_model(request: Request):
    return request.app.state.workspace.model_settings()


@router.post("/model")
def save_model(request: Request, body: ModelIn | None = None):
    incoming = body or ModelIn()
    return _respond(
        request.app.state.workspace.configure_model(
            incoming.name, incoming.base_url, incoming.api_key
        )
    )


@router.post("/instructions")
def start_instruction(request: Request, body: InstructionIn | None = None):
    incoming = body or InstructionIn()
    return _respond(
        request.app.state.workspace.start_instruction(
            incoming.title,
            incoming.goal,
            incoming.criterion,
            incoming.project,
            incoming.read_path,
            incoming.file,
            incoming.change_class,
            incoming.what_changed,
        )
    )


@router.get("/tasks")
def list_tasks(request: Request):
    return request.app.state.workspace.list_tasks()


@router.post("/tasks")
def create_task(request: Request, body: CreateTask):
    return _respond(request.app.state.workspace.create_task(body.title))


@router.get("/tasks/{task_id}")
def read_task(request: Request, task_id: int):
    return _respond(request.app.state.workspace.get_task(task_id))


@router.patch("/tasks/{task_id}")
def set_goal(request: Request, task_id: int, body: GoalUpdate):
    return _respond(request.app.state.workspace.set_goal(task_id, body.goal))


@router.post("/tasks/{task_id}/criteria")
def add_criterion(request: Request, task_id: int, body: CriterionText):
    return _respond(request.app.state.workspace.add_criterion(task_id, body.text))


@router.patch("/tasks/{task_id}/criteria/{criterion_id}")
def update_criterion(request: Request, task_id: int, criterion_id: int, body: CriterionText):
    return _respond(request.app.state.workspace.update_criterion(task_id, criterion_id, body.text))


@router.delete("/tasks/{task_id}/criteria/{criterion_id}")
def remove_criterion(request: Request, task_id: int, criterion_id: int):
    return _respond(request.app.state.workspace.remove_criterion(task_id, criterion_id))


@router.post("/tasks/{task_id}/transitions")
def transition(request: Request, task_id: int, body: TransitionIn):
    return _respond(request.app.state.workspace.transition(task_id, body.action, body.reason))


@router.post("/tasks/{task_id}/criteria/{criterion_id}/verify")
def verify(request: Request, task_id: int, criterion_id: int, body: VerifyIn):
    return _respond(
        request.app.state.workspace.verify_criterion(
            task_id,
            criterion_id,
            body.observation,
            body.pass_result,
            body.method,
            body.run_identifier,
        )
    )


@router.post("/tasks/{task_id}/criteria/{criterion_id}/unverify")
def unverify(request: Request, task_id: int, criterion_id: int):
    return _respond(request.app.state.workspace.unverify_criterion(task_id, criterion_id))


@router.post("/tasks/{task_id}/prerequisites")
def add_prerequisite(request: Request, task_id: int, body: PrerequisiteIn):
    return _respond(
        request.app.state.workspace.add_prerequisite(task_id, body.prerequisite_id)
    )


@router.post("/tasks/{task_id}/prerequisites/{prerequisite_id}/remove")
def remove_prerequisite(request: Request, task_id: int, prerequisite_id: int):
    return _respond(
        request.app.state.workspace.remove_prerequisite(task_id, prerequisite_id)
    )


@router.post("/tasks/{task_id}/workflow-steps")
def add_workflow_step(request: Request, task_id: int, body: WorkflowStepIn):
    return _respond(
        request.app.state.workspace.add_workflow_step(
            task_id,
            body.title,
            body.action,
            body.project,
            body.path,
            body.what_changed,
            body.change_class,
        )
    )


@router.post("/tasks/{task_id}/workflow-steps/{step_id}/remove")
def remove_workflow_step(request: Request, task_id: int, step_id: int):
    return _respond(request.app.state.workspace.remove_workflow_step(task_id, step_id))


@router.post("/tasks/{task_id}/workflow/advance")
def advance_workflow(request: Request, task_id: int, body: AdvanceIn | None = None):
    name = "" if body is None else body.name
    return _respond(request.app.state.workspace.advance_workflow(task_id, name))


@router.post("/tasks/{task_id}/workflow/recover")
def recover_workflow(request: Request, task_id: int):
    return _respond(request.app.state.workspace.recover_workflow(task_id))


@router.post("/tasks/{task_id}/workflow/revise")
def revise_workflow(request: Request, task_id: int):
    return _respond(request.app.state.workspace.revise_workflow(task_id))


@router.post("/tasks/{task_id}/workflow/migrate")
def migrate_workflow(request: Request, task_id: int, body: MigrateIn):
    return _respond(request.app.state.workspace.migrate_workflow(task_id, body.reason))


@router.get("/tasks/{task_id}/workflow-replay")
def workflow_replay(request: Request, task_id: int):
    return _respond(request.app.state.workspace.workflow_replay(task_id))


@router.post("/tasks/{task_id}/workflow/replay-execution")
def replay_workflow_execution(request: Request, task_id: int):
    return _respond(request.app.state.workspace.replay_workflow_execution(task_id))


@router.post("/tasks/{task_id}/subtasks")
def add_subtask(request: Request, task_id: int, body: SubtaskIn):
    return _respond(request.app.state.workspace.add_subtask(task_id, body.title))


@router.post("/tasks/{task_id}/implementation-changes")
def record_change(request: Request, task_id: int, body: ImplementationChangeIn):
    return _respond(
        request.app.state.workspace.record_change(task_id, body.what_changed, body.change_class)
    )


@router.post("/tasks/{task_id}/model-files")
def record_model_file(request: Request, task_id: int, body: ModelFileIn):
    return _respond(
        request.app.state.workspace.record_model_file(
            task_id,
            body.project,
            body.change_class,
            body.what_changed,
            body.stopped,
            body.file,
            body.file_read_id,
        )
    )


@router.post("/tasks/{task_id}/file-reads")
def record_file_read(request: Request, task_id: int, body: FileReadIn):
    return _respond(
        request.app.state.workspace.record_file_read(task_id, body.project, body.file)
    )


@router.post("/tasks/{task_id}/folders")
def record_folder(request: Request, task_id: int, body: FolderIn):
    return _respond(
        request.app.state.workspace.record_folder(
            task_id,
            body.project,
            body.change_class,
            body.what_changed,
            body.stopped,
            body.folder,
        )
    )


@router.post("/tasks/{task_id}/test-runs")
def record_test(request: Request, task_id: int, body: TestRunIn):
    return _respond(
        request.app.state.workspace.record_test(
            task_id,
            body.project,
            body.change_class,
            body.what_changed,
            body.stopped,
            body.test,
        )
    )


@router.post("/tasks/{task_id}/pull-requests")
def record_pull_request(request: Request, task_id: int, body: PullRequestIn):
    return _respond(
        request.app.state.workspace.record_pull_request(
            task_id,
            body.project,
            body.change_class,
            body.what_changed,
            body.stopped,
            body.branch,
        )
    )


@router.post("/tasks/{task_id}/branches")
def record_branch(request: Request, task_id: int, body: CreateBranchIn):
    return _respond(
        request.app.state.workspace.record_branch(
            task_id,
            body.project,
            body.change_class,
            body.what_changed,
            body.stopped,
            body.branch,
        )
    )


@router.post("/tasks/{task_id}/commits")
def record_commit(request: Request, task_id: int, body: CommitFileIn):
    return _respond(
        request.app.state.workspace.record_commit(
            task_id,
            body.project,
            body.change_class,
            body.what_changed,
            body.stopped,
            body.file,
        )
    )


@router.post("/tasks/{task_id}/deletes")
def record_deletion(request: Request, task_id: int, body: DeleteFileIn):
    return _respond(
        request.app.state.workspace.record_deletion(
            task_id,
            body.project,
            body.change_class,
            body.what_changed,
            body.stopped,
            body.file,
        )
    )


@router.post("/tasks/{task_id}/assistant-changes")
def record_assistant_change(request: Request, task_id: int, body: AssistantChangeIn):
    return _respond(
        request.app.state.workspace.record_assistant_change(
            task_id,
            body.project,
            body.change_class,
            body.what_changed,
            body.stopped,
            body.file,
            "" if body.file is not None and body.file_text is None else body.file_text,
        )
    )


@router.post("/tasks/{task_id}/implementation-changes/{change_id}/approve")
def approve_change(request: Request, task_id: int, change_id: int, body: ApprovalIn):
    return _respond(
        request.app.state.workspace.approve_change(
            task_id, change_id, body.evidence, body.actor
        )
    )


@router.post("/tasks/{task_id}/implementation-changes/{change_id}/not-carried-out")
def mark_not_carried_out(request: Request, task_id: int, change_id: int, body: NotCarriedOutIn):
    return _respond(
        request.app.state.workspace.mark_change_not_carried_out(
            task_id, change_id, body.reason, body.actor
        )
    )


@router.post("/tasks/{task_id}/assistant-checks")
def record_assistant_check(request: Request, task_id: int, body: AssistantCheckIn):
    return _respond(
        request.app.state.workspace.record_assistant_check(
            task_id, body.change_id, body.criterion_id, body.evidence, body.result
        )
    )


@router.post("/tasks/{task_id}/implementation-changes/{change_id}/checks")
def record_check(request: Request, task_id: int, change_id: int, body: CheckIn):
    return _respond(
        request.app.state.workspace.record_check(
            task_id, change_id, body.criterion_id, body.evidence, body.result
        )
    )


@router.post("/tasks/{task_id}/decisions")
def add_decision(request: Request, task_id: int, body: DecisionIn):
    return _respond(
        request.app.state.workspace.add_decision(
            task_id, body.statement, body.rationale, body.supersedes
        )
    )


@router.post("/tasks/{task_id}/linked-decisions")
def add_linked_decision(request: Request, task_id: int, body: LinkedDecisionIn):
    return _respond(
        request.app.state.workspace.add_linked_decision(
            task_id, body.statement, body.rationale, body.check_id, body.supersedes
        )
    )


class RequirementIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    statement: str
    kind: str | None = None


class TaskLinkIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    task_id: int


class CriterionLinkIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    task_id: int
    criterion_id: int


class RequirementCheckIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str


class RequirementRunIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    check: str
    result: str | None = None
    run_identifier: str = ""


@router.get("/traceability")
def traceability(request: Request):
    return request.app.state.workspace.traceability()


@router.get("/requirements")
def list_requirements(request: Request):
    return request.app.state.workspace.list_requirements()


@router.post("/requirements")
def record_requirement(request: Request, body: RequirementIn):
    return _respond(request.app.state.workspace.record_requirement(body.statement, body.kind))


@router.get("/requirements/{requirement_id}")
def read_requirement(request: Request, requirement_id: int):
    return _respond(request.app.state.workspace.get_requirement(requirement_id))


@router.post("/requirements/{requirement_id}")
def change_requirement(request: Request, requirement_id: int, body: RequirementIn):
    return _respond(
        request.app.state.workspace.change_requirement(
            requirement_id, body.statement, body.kind
        )
    )


@router.post("/requirements/{requirement_id}/tasks")
def link_requirement_task(request: Request, requirement_id: int, body: TaskLinkIn):
    return _respond(
        request.app.state.workspace.link_requirement_task(requirement_id, body.task_id)
    )


@router.post("/requirements/{requirement_id}/criteria")
def link_requirement_criterion(request: Request, requirement_id: int, body: CriterionLinkIn):
    return _respond(
        request.app.state.workspace.link_requirement_criterion(
            requirement_id, body.task_id, body.criterion_id
        )
    )


@router.post("/requirements/{requirement_id}/tasks/{task_id}/unlink")
def unlink_requirement_task(request: Request, requirement_id: int, task_id: int):
    return _respond(
        request.app.state.workspace.unlink_requirement_task(requirement_id, task_id)
    )


@router.post("/requirements/{requirement_id}/criteria/{criterion_id}/unlink")
def unlink_requirement_criterion(request: Request, requirement_id: int, criterion_id: int):
    return _respond(
        request.app.state.workspace.unlink_requirement_criterion(requirement_id, criterion_id)
    )


@router.post("/requirements/{requirement_id}/checks")
def name_requirement_check(request: Request, requirement_id: int, body: RequirementCheckIn):
    return _respond(
        request.app.state.workspace.name_requirement_check(requirement_id, body.name)
    )


@router.post("/requirements/{requirement_id}/checks/{check_id}/remove")
def remove_requirement_check(request: Request, requirement_id: int, check_id: int):
    return _respond(
        request.app.state.workspace.remove_requirement_check(requirement_id, check_id)
    )


@router.post("/requirements/{requirement_id}/runs")
def record_requirement_run(request: Request, requirement_id: int, body: RequirementRunIn):
    return _respond(
        request.app.state.workspace.record_requirement_run(
            requirement_id, body.check, body.result, body.run_identifier
        )
    )
