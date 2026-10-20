# Commands: Safe Exploration, Causal Inference, and Counterfactual Evaluation

## Name action

`POST /api/tasks/{task_id}/safe-actions`

`POST /tasks/{task_id}/safe-actions`

```json
{ "name": "ada", "risk": "1" }
```

`name` and `risk` may be omitted. The page fields are Action name, `id="safe-action-name"`, and Risk, `id="action-risk"`. The button is Name action.

The trimmed name is stored once at the given risk. The risk is accepted only when the trimmed text is `1` or `2`. The same name returns the task detail and does not change the risk. A task stores at most 2 actions. A new action removes the stored effect.

## Record probe

`POST /api/tasks/{task_id}/safe-probes`

`POST /tasks/{task_id}/safe-probes`

```json
{ "name": "one", "state": "rush", "action": "ada", "reward": "1" }
```

`name`, `state`, `action`, and `reward` may be omitted. The page fields are Probe name, `id="probe-name"`, State, `id="probe-state"`, Action, `id="probe-action"`, and Reward, `id="probe-reward"`. The button is Record probe.

The trimmed name is stored once for the trimmed state and the trimmed action, with the given reward. The reward is accepted only when the trimmed text is `1` or `2`. The action must be on this task and its risk must be 1. The same name returns the task detail and does not change the probe. A task stores at most 4 probes. A new probe removes the stored effect.

## Compare actions

`POST /api/tasks/{task_id}/safe-effects`

`POST /tasks/{task_id}/safe-effects`

```json
{ "state": "rush", "action": "grace", "instead": "ada" }
```

`state`, `action`, and `instead` may be omitted. The page fields are State, `id="effect-state"`, Action, `id="effect-action"`, and Instead, `id="effect-instead"`. The button is Compare actions.

The command stores one effect. It uses the earliest probe of `action` in `state` and the earliest probe of `instead` in `state`. The effect is the first reward minus the second.

## Task detail

The task detail includes `safety`:

```json
{
  "actions": [
    { "name": "ada", "risk": 1 },
    { "name": "grace", "risk": 1 }
  ],
  "probes": [
    { "name": "one", "state": "rush", "action": "ada", "reward": 1 },
    { "name": "two", "state": "rush", "action": "grace", "reward": 2 }
  ],
  "effect": { "state": "rush", "action": "grace", "instead": "ada", "effect": 1 },
  "can_name": true,
  "can_probe": true,
  "can_compare": true
}
```

`actions` and `probes` are oldest first. `effect` is null when no effect is stored. `can_name` is true while the task is In Progress. `can_probe` is true while the task is In Progress and at least one action has risk 1. `can_compare` is true while the task is In Progress and at least two probes exist.

## Page

The task page shows a Safety section.

- Each action is `ada: risk 1` in `id="safe-actions"`.
- Each probe is `one: rush, ada, reward 1` in `id="safe-probes"`.
- The effect is `Effect of grace instead of ada in rush: 1` in `id="safe-effect"`.
- Name action is offered while the task is In Progress.
- Record probe is offered only while `can_probe` is true.
- Compare actions is offered only while `can_compare` is true.
- When no action exists, the section says `No actions yet.`

## Refusals

| Condition | Status | Message |
|---|---|---|
| Blank action name | 400 | `Name this action.` |
| Risk is not 1 or 2 | 400 | `Name a risk of 1 or 2.` |
| The task already has 2 actions | 409 | `This task already has 2 actions.` |
| Blank probe name | 400 | `Name this probe.` |
| Blank probe state | 400 | `Name the state.` |
| Blank probe action | 400 | `Name the action.` |
| Reward is not 1 or 2 | 400 | `Name a reward of 1 or 2.` |
| The action is not on this task | 409 | `That action is not on this task.` |
| The action risk is 2 | 409 | `That action is not safe to explore.` |
| The task already has 4 probes | 409 | `This task already has 4 probes.` |
| No probe has been recorded | 409 | `Name a probe first.` |
| Blank comparison state | 400 | `Name the state to compare.` |
| Blank comparison action | 400 | `Name the action.` |
| Blank replaced action | 400 | `Name the action it replaces.` |
| An action replaces itself | 409 | `An action cannot replace itself.` |
| Either action has no probe in the state | 409 | `That comparison needs both actions in this state.` |
| Task is not In Progress | 409 | `The task must be In Progress.` |
| Task is missing | 404 | `Task not found.` |

A repeated action name or a repeated probe name returns the task detail with status 200.
