# Commands: Offline Reinforcement Learning and Policy Evaluation

## Record logged step

`POST /api/tasks/{task_id}/policy-logs`

`POST /tasks/{task_id}/policy-logs`

```json
{ "name": "one", "state": "rush", "action": "ada", "reward": "1" }
```

`name`, `state`, `action`, and `reward` may be omitted. The page fields are Step name, `id="log-name"`, State, `id="log-state"`, Action, `id="log-action"`, and Reward, `id="log-reward"`. The button is Record logged step.

The trimmed name is stored once with the trimmed state, the trimmed action, and the given reward. The reward is accepted only when the trimmed text is `1` or `2`. The same name returns the task detail and does not change the step. A task stores at most 4 logged steps. A new step removes the stored score.

## Name policy rule

`POST /api/tasks/{task_id}/policy-rules`

`POST /tasks/{task_id}/policy-rules`

```json
{ "state": "rush", "action": "grace" }
```

`state` and `action` may be omitted. The page fields are State, `id="rule-state"`, and Action, `id="rule-action"`. The button is Name policy rule.

The trimmed state must appear in a logged step on this task. The trimmed action is the action the policy takes in that state. The same state and the same action return the task detail and do not store another rule. A different action replaces the stored action and removes the score.

## Evaluate policy

`POST /api/tasks/{task_id}/policy-scores`

`POST /tasks/{task_id}/policy-scores`

The body may be empty. The button is Evaluate policy.

The command stores one score. A logged step counts only when its state has a rule and its action is the action that rule names. The score stores the total of those rewards and the number of those steps.

## Task detail

The task detail includes `evaluation`:

```json
{
  "logs": [
    { "name": "one", "state": "rush", "action": "ada", "reward": 1 },
    { "name": "two", "state": "rush", "action": "grace", "reward": 2 },
    { "name": "three", "state": "quiet", "action": "ada", "reward": 2 }
  ],
  "rules": [
    { "state": "rush", "action": "grace" },
    { "state": "quiet", "action": "ada" }
  ],
  "score": { "total": 4, "count": 2 },
  "can_log": true,
  "can_rule": true,
  "can_evaluate": true
}
```

`logs` and `rules` are oldest first. `score` is null when no score is stored. `can_log` is true while the task is In Progress. `can_rule` is true while the task is In Progress and at least one logged step exists. `can_evaluate` is true while the task is In Progress and at least one rule exists.

## Page

The task page shows a Policy section.

- Each logged step is `one: rush, ada, reward 1` in `id="policy-logs"`.
- Each rule is `rush: grace` in `id="policy-rules"`.
- The score is `Score: 4 from 2` in `id="policy-score"`.
- Record logged step is offered while the task is In Progress.
- Name policy rule is offered only while `can_rule` is true.
- Evaluate policy is offered only while `can_evaluate` is true.
- When no logged step exists, the section says `No logged steps yet.`

## Refusals

| Condition | Status | Message |
|---|---|---|
| Blank step name | 400 | `Name this step.` |
| Blank step state | 400 | `Name the state.` |
| Blank step action | 400 | `Name the action.` |
| Reward is not 1 or 2 | 400 | `Name a reward of 1 or 2.` |
| The task already has 4 logged steps | 409 | `This task already has 4 logged steps.` |
| Blank rule state | 400 | `Name the state for this rule.` |
| Blank rule action | 400 | `Name the action for this rule.` |
| No logged step has been recorded | 409 | `Name a logged step first.` |
| The state is not in the log | 409 | `That state is not in the log.` |
| No policy rule has been named | 409 | `Name a policy rule first.` |
| No logged step matches the policy | 409 | `No logged step matches this policy.` |
| Task is not In Progress | 409 | `The task must be In Progress.` |
| Task is missing | 404 | `Task not found.` |

A repeated step name, or the same state with the same action, returns the task detail with status 200.
