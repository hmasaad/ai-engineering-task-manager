"""JSON commands. The pages call the same workspace methods."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from task_manager.domain.results import Refusal

router = APIRouter(prefix="/api")


class CreateTask(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str


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


class SubtaskIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str


class DecisionIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    statement: str
    rationale: str
    supersedes: list[int] = Field(default_factory=list)


def _respond(result):
    if isinstance(result, Refusal):
        return JSONResponse(status_code=result.code, content=result.body)
    return result


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
            task_id, criterion_id, body.observation, body.pass_result
        )
    )


@router.post("/tasks/{task_id}/criteria/{criterion_id}/unverify")
def unverify(request: Request, task_id: int, criterion_id: int):
    return _respond(request.app.state.workspace.unverify_criterion(task_id, criterion_id))


@router.post("/tasks/{task_id}/subtasks")
def add_subtask(request: Request, task_id: int, body: SubtaskIn):
    return _respond(request.app.state.workspace.add_subtask(task_id, body.title))


@router.post("/tasks/{task_id}/decisions")
def add_decision(request: Request, task_id: int, body: DecisionIn):
    return _respond(
        request.app.state.workspace.add_decision(
            task_id, body.statement, body.rationale, body.supersedes
        )
    )
