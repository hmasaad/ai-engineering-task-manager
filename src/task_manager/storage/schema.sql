PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS workspace (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    engineer_name TEXT NOT NULL CHECK (length(trim(engineer_name)) > 0)
);

CREATE TABLE IF NOT EXISTS configured_model (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    model_name TEXT NOT NULL CHECK (length(trim(model_name)) > 0),
    model_text TEXT NOT NULL CHECK (length(trim(model_text)) > 0)
);

CREATE TABLE IF NOT EXISTS model_service (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    model_name TEXT NOT NULL CHECK (length(trim(model_name)) > 0),
    base_url TEXT NOT NULL CHECK (length(trim(base_url)) > 0),
    api_key TEXT CHECK (api_key IS NULL OR length(trim(api_key)) > 0)
);

CREATE TABLE IF NOT EXISTS task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    goal TEXT CHECK (goal IS NULL OR length(trim(goal)) > 0),
    status TEXT NOT NULL CHECK (status IN ('Draft', 'Ready', 'In Progress', 'Completed', 'Cancelled')),
    parent_id INTEGER REFERENCES task(id),
    created_at TEXT NOT NULL,
    cancel_reason TEXT,
    CHECK (
        (status = 'Cancelled' AND cancel_reason IS NOT NULL AND length(trim(cancel_reason)) > 0)
        OR (status != 'Cancelled' AND cancel_reason IS NULL)
    )
);

CREATE TABLE IF NOT EXISTS acceptance_criterion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    text TEXT NOT NULL CHECK (length(trim(text)) > 0),
    position INTEGER NOT NULL,
    observation TEXT,
    pass_result TEXT CHECK (pass_result IS NULL OR pass_result = 'pass'),
    verified_at TEXT,
    provider_name TEXT,
    CHECK (
        (
            observation IS NULL
            AND pass_result IS NULL
            AND verified_at IS NULL
            AND provider_name IS NULL
        )
        OR (
            observation IS NOT NULL AND length(trim(observation)) > 0
            AND pass_result = 'pass'
            AND verified_at IS NOT NULL
            AND provider_name IS NOT NULL AND length(trim(provider_name)) > 0
        )
    )
);

CREATE TABLE IF NOT EXISTS status_change (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    from_status TEXT NOT NULL,
    to_status TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    cause_code TEXT NOT NULL,
    cause_detail TEXT
);

CREATE TABLE IF NOT EXISTS implementation_decision (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    statement TEXT NOT NULL CHECK (length(trim(statement)) > 0),
    rationale TEXT NOT NULL CHECK (length(trim(rationale)) > 0),
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decision_supersedes (
    decision_id INTEGER NOT NULL REFERENCES implementation_decision(id),
    earlier_decision_id INTEGER NOT NULL REFERENCES implementation_decision(id),
    PRIMARY KEY (decision_id, earlier_decision_id),
    CHECK (decision_id != earlier_decision_id)
);

CREATE INDEX IF NOT EXISTS idx_task_parent ON task(parent_id);
CREATE INDEX IF NOT EXISTS idx_criterion_task ON acceptance_criterion(task_id);
CREATE INDEX IF NOT EXISTS idx_status_change_task ON status_change(task_id);
CREATE INDEX IF NOT EXISTS idx_decision_task ON implementation_decision(task_id);

CREATE TABLE IF NOT EXISTS implementation_change (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    what_changed TEXT NOT NULL CHECK (length(trim(what_changed)) > 0),
    class TEXT NOT NULL CHECK (class IN ('ordinary', 'consequential')),
    engineer_name TEXT NOT NULL CHECK (length(trim(engineer_name)) > 0),
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS implementation_resolution (
    change_id INTEGER PRIMARY KEY REFERENCES implementation_change(id),
    kind TEXT NOT NULL CHECK (kind IN ('approved', 'not_carried_out')),
    evidence TEXT,
    reason TEXT,
    engineer_name TEXT NOT NULL CHECK (length(trim(engineer_name)) > 0),
    resolved_at TEXT NOT NULL,
    CHECK (
        (
            kind = 'approved'
            AND evidence IS NOT NULL AND length(trim(evidence)) > 0
            AND reason IS NULL
        )
        OR (
            kind = 'not_carried_out'
            AND reason IS NOT NULL AND length(trim(reason)) > 0
            AND evidence IS NULL
        )
    )
);

CREATE INDEX IF NOT EXISTS idx_implementation_change_task ON implementation_change(task_id);

CREATE TABLE IF NOT EXISTS implementation_check (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    change_id INTEGER NOT NULL REFERENCES implementation_change(id),
    criterion_id INTEGER NOT NULL,
    criterion_text TEXT NOT NULL CHECK (length(trim(criterion_text)) > 0),
    evidence TEXT NOT NULL CHECK (length(trim(evidence)) > 0),
    result TEXT NOT NULL CHECK (result IN ('passed', 'failed')),
    engineer_name TEXT NOT NULL CHECK (length(trim(engineer_name)) > 0),
    checked_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_implementation_check_change ON implementation_check(change_id);

CREATE TABLE IF NOT EXISTS assistant_check (
    check_id INTEGER PRIMARY KEY REFERENCES implementation_check(id),
    assistant_name TEXT NOT NULL CHECK (length(trim(assistant_name)) > 0)
);

CREATE TABLE IF NOT EXISTS workspace_assistant (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    assistant_name TEXT NOT NULL CHECK (length(trim(assistant_name)) > 0)
);

CREATE TABLE IF NOT EXISTS assistant_change (
    change_id INTEGER PRIMARY KEY REFERENCES implementation_change(id),
    project TEXT NOT NULL CHECK (length(trim(project)) > 0),
    assistant_name TEXT NOT NULL CHECK (length(trim(assistant_name)) > 0),
    stopped INTEGER NOT NULL CHECK (stopped IN (0, 1))
);

CREATE TABLE IF NOT EXISTS applied_file (
    change_id INTEGER PRIMARY KEY REFERENCES implementation_change(id),
    file_path TEXT NOT NULL CHECK (length(trim(file_path)) > 0),
    was_new INTEGER NOT NULL CHECK (was_new IN (0, 1)),
    previous_text TEXT,
    file_text TEXT NOT NULL,
    CHECK (
        (was_new = 1 AND previous_text IS NULL)
        OR (was_new = 0 AND previous_text IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS created_folder (
    change_id INTEGER PRIMARY KEY REFERENCES implementation_change(id),
    folder_path TEXT NOT NULL CHECK (length(trim(folder_path)) > 0)
);

CREATE TABLE IF NOT EXISTS test_run (
    change_id INTEGER PRIMARY KEY REFERENCES implementation_change(id),
    test_path TEXT NOT NULL CHECK (length(trim(test_path)) > 0)
);

CREATE TABLE IF NOT EXISTS test_run_result (
    change_id INTEGER PRIMARY KEY REFERENCES test_run(change_id),
    result TEXT NOT NULL CHECK (result IN ('passed', 'failed')),
    output TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS deleted_file (
    change_id INTEGER PRIMARY KEY REFERENCES implementation_change(id),
    file_path TEXT NOT NULL CHECK (length(trim(file_path)) > 0),
    previous_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS committed_file (
    change_id INTEGER PRIMARY KEY REFERENCES implementation_change(id),
    file_path TEXT NOT NULL CHECK (length(trim(file_path)) > 0),
    file_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS committed_revision (
    change_id INTEGER PRIMARY KEY REFERENCES committed_file(change_id),
    commit_hash TEXT NOT NULL CHECK (length(trim(commit_hash)) > 0)
);

CREATE TABLE IF NOT EXISTS pull_request (
    change_id INTEGER PRIMARY KEY REFERENCES implementation_change(id),
    branch TEXT NOT NULL CHECK (length(trim(branch)) > 0),
    base_branch TEXT NOT NULL CHECK (length(trim(base_branch)) > 0)
);

CREATE TABLE IF NOT EXISTS pull_request_result (
    change_id INTEGER PRIMARY KEY REFERENCES pull_request(change_id),
    pull_url TEXT NOT NULL CHECK (length(trim(pull_url)) > 0)
);

CREATE TABLE IF NOT EXISTS created_branch (
    change_id INTEGER PRIMARY KEY REFERENCES implementation_change(id),
    branch TEXT NOT NULL CHECK (length(trim(branch)) > 0),
    start_commit TEXT NOT NULL CHECK (length(trim(start_commit)) > 0)
);

CREATE TABLE IF NOT EXISTS created_branch_checkout (
    change_id INTEGER PRIMARY KEY REFERENCES created_branch(change_id)
);

CREATE TABLE IF NOT EXISTS decision_check (
    decision_id INTEGER PRIMARY KEY REFERENCES implementation_decision(id),
    check_id INTEGER NOT NULL REFERENCES implementation_check(id)
);

CREATE TABLE IF NOT EXISTS file_read (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    project TEXT NOT NULL CHECK (length(trim(project)) > 0),
    file_path TEXT NOT NULL CHECK (length(trim(file_path)) > 0),
    file_text TEXT NOT NULL,
    assistant_name TEXT NOT NULL CHECK (length(trim(assistant_name)) > 0),
    read_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_file_read_task ON file_read(task_id, read_at, id);

CREATE TABLE IF NOT EXISTS model_call (
    change_id INTEGER PRIMARY KEY REFERENCES implementation_change(id),
    file_read_id INTEGER NOT NULL REFERENCES file_read(id),
    model_name TEXT NOT NULL CHECK (length(trim(model_name)) > 0),
    model_input TEXT NOT NULL CHECK (length(model_input) > 0),
    model_output TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS requirement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL CHECK (kind IN ('functional', 'non-functional')),
    statement TEXT NOT NULL CHECK (length(trim(statement)) > 0),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS requirement_task (
    requirement_id INTEGER NOT NULL REFERENCES requirement(id),
    task_id INTEGER NOT NULL REFERENCES task(id),
    PRIMARY KEY (requirement_id, task_id)
);

CREATE INDEX IF NOT EXISTS idx_requirement_task_task ON requirement_task(task_id);

CREATE TABLE IF NOT EXISTS requirement_criterion (
    requirement_id INTEGER NOT NULL REFERENCES requirement(id),
    criterion_id INTEGER NOT NULL REFERENCES acceptance_criterion(id) ON DELETE CASCADE,
    PRIMARY KEY (requirement_id, criterion_id)
);

CREATE TABLE IF NOT EXISTS requirement_check (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_id INTEGER NOT NULL REFERENCES requirement(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    removed_at TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_requirement_check_active_name
    ON requirement_check(requirement_id, name)
    WHERE removed_at IS NULL;

CREATE TABLE IF NOT EXISTS verification_run (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    check_id INTEGER NOT NULL REFERENCES requirement_check(id),
    result TEXT NOT NULL CHECK (result IN ('passed', 'failed')),
    run_identifier TEXT NOT NULL CHECK (length(trim(run_identifier)) > 0),
    engineer_name TEXT NOT NULL CHECK (length(trim(engineer_name)) > 0),
    recorded_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_verification_run_check
    ON verification_run(check_id, recorded_at, id);

CREATE TABLE IF NOT EXISTS criterion_evidence (
    criterion_id INTEGER PRIMARY KEY REFERENCES acceptance_criterion(id) ON DELETE CASCADE,
    method TEXT NOT NULL CHECK (length(trim(method)) > 0),
    run_identifier TEXT NOT NULL CHECK (length(trim(run_identifier)) > 0)
);

CREATE TABLE IF NOT EXISTS task_dependency (
    task_id INTEGER NOT NULL REFERENCES task(id),
    prerequisite_id INTEGER NOT NULL REFERENCES task(id),
    PRIMARY KEY (task_id, prerequisite_id),
    CHECK (task_id != prerequisite_id)
);

CREATE INDEX IF NOT EXISTS idx_task_dependency_prerequisite
    ON task_dependency(prerequisite_id);

CREATE TABLE IF NOT EXISTS workflow_step (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    position INTEGER NOT NULL,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    action TEXT NOT NULL CHECK (action IN ('read', 'folder')),
    project TEXT NOT NULL CHECK (length(trim(project)) > 0),
    path TEXT NOT NULL CHECK (length(trim(path)) > 0),
    what_changed TEXT,
    change_class TEXT,
    state TEXT NOT NULL CHECK (state IN ('Pending', 'Running', 'Completed', 'Waiting', 'Failed')),
    detail TEXT,
    change_id INTEGER REFERENCES implementation_change(id),
    CHECK (
        (
            action = 'read'
            AND what_changed IS NULL
            AND change_class IS NULL
        )
        OR (
            action = 'folder'
            AND what_changed IS NOT NULL AND length(trim(what_changed)) > 0
            AND change_class IN ('ordinary', 'consequential')
        )
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_workflow_step_task_position
    ON workflow_step(task_id, position);

CREATE TABLE IF NOT EXISTS workflow_attempt (
    step_id INTEGER PRIMARY KEY REFERENCES workflow_step(id),
    effect_before INTEGER NOT NULL CHECK (effect_before >= 0)
);

CREATE TABLE IF NOT EXISTS workflow_event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    step_id INTEGER NOT NULL REFERENCES workflow_step(id),
    state TEXT NOT NULL CHECK (state IN ('Running', 'Completed', 'Waiting', 'Failed')),
    detail TEXT,
    recorded_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_workflow_event_task
    ON workflow_event(task_id, id);

CREATE TABLE IF NOT EXISTS workflow_advance (
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    step_id INTEGER NOT NULL REFERENCES workflow_step(id),
    PRIMARY KEY (task_id, name)
);

CREATE TABLE IF NOT EXISTS workflow_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    number INTEGER NOT NULL CHECK (number >= 1),
    state TEXT NOT NULL CHECK (state IN ('Current', 'Draft', 'Superseded')),
    UNIQUE (task_id, number)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_workflow_version_current
    ON workflow_version(task_id)
    WHERE state = 'Current';

CREATE UNIQUE INDEX IF NOT EXISTS idx_workflow_version_draft
    ON workflow_version(task_id)
    WHERE state = 'Draft';

CREATE TABLE IF NOT EXISTS workflow_version_step (
    version_id INTEGER NOT NULL REFERENCES workflow_version(id),
    step_id INTEGER NOT NULL REFERENCES workflow_step(id),
    position INTEGER NOT NULL CHECK (position >= 1),
    PRIMARY KEY (version_id, step_id),
    UNIQUE (version_id, position)
);

CREATE TABLE IF NOT EXISTS workflow_migration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    from_version_id INTEGER NOT NULL REFERENCES workflow_version(id),
    to_version_id INTEGER NOT NULL REFERENCES workflow_version(id),
    reason TEXT NOT NULL CHECK (length(trim(reason)) > 0),
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workflow_outbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    step_id INTEGER NOT NULL UNIQUE REFERENCES workflow_step(id),
    effect TEXT NOT NULL CHECK (length(trim(effect)) > 0),
    state TEXT NOT NULL CHECK (state IN ('Pending', 'Delivered')),
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workflow_inbox (
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    outbox_id INTEGER NOT NULL REFERENCES workflow_outbox(id),
    recorded_at TEXT NOT NULL,
    PRIMARY KEY (task_id, name)
);

CREATE TABLE IF NOT EXISTS workflow_compensation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    step_id INTEGER NOT NULL UNIQUE REFERENCES workflow_step(id),
    reason TEXT NOT NULL CHECK (length(trim(reason)) > 0),
    state TEXT NOT NULL CHECK (state IN ('Compensated', 'Waiting', 'Not carried out')),
    evidence TEXT CHECK (evidence IS NULL OR length(trim(evidence)) > 0),
    decline_reason TEXT CHECK (decline_reason IS NULL OR length(trim(decline_reason)) > 0),
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workflow_poison (
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    outbox_id INTEGER NOT NULL REFERENCES workflow_outbox(id),
    reason TEXT NOT NULL CHECK (length(trim(reason)) > 0),
    recorded_at TEXT NOT NULL,
    PRIMARY KEY (task_id, name)
);

CREATE TABLE IF NOT EXISTS workflow_dead_letter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    outbox_id INTEGER NOT NULL UNIQUE REFERENCES workflow_outbox(id),
    reason TEXT NOT NULL CHECK (length(trim(reason)) > 0),
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workflow_delivery_retry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    outbox_id INTEGER NOT NULL REFERENCES workflow_outbox(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    next_eligible_at TEXT NOT NULL CHECK (length(trim(next_eligible_at)) > 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS workflow_dead_letter_replay (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    outbox_id INTEGER NOT NULL UNIQUE REFERENCES workflow_outbox(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS workflow_trace (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL UNIQUE REFERENCES task(id),
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workflow_span (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id INTEGER NOT NULL REFERENCES workflow_trace(id),
    step_id INTEGER NOT NULL REFERENCES workflow_step(id),
    parent_id INTEGER REFERENCES workflow_span(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    state TEXT NOT NULL CHECK (state IN ('Running', 'Completed', 'Failed', 'Waiting')),
    detail TEXT CHECK (detail IS NULL OR length(trim(detail)) > 0),
    started_at TEXT NOT NULL,
    ended_at TEXT
);

CREATE TABLE IF NOT EXISTS workflow_checkpoint (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS workflow_checkpoint_step (
    checkpoint_id INTEGER NOT NULL REFERENCES workflow_checkpoint(id),
    step_id INTEGER NOT NULL REFERENCES workflow_step(id),
    position INTEGER NOT NULL CHECK (position >= 1),
    state TEXT NOT NULL CHECK (state IN ('Pending', 'Completed', 'Failed', 'Waiting')),
    detail TEXT CHECK (detail IS NULL OR length(trim(detail)) > 0),
    PRIMARY KEY (checkpoint_id, step_id)
);

CREATE TABLE IF NOT EXISTS workflow_isolated_effect (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    step_id INTEGER NOT NULL UNIQUE REFERENCES workflow_step(id),
    effect TEXT NOT NULL CHECK (length(trim(effect)) > 0),
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workflow_file_run (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    step_id INTEGER NOT NULL REFERENCES workflow_step(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS command_execution (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    action TEXT NOT NULL CHECK (action IN ('read', 'folder')),
    path TEXT NOT NULL CHECK (length(trim(path)) > 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS work_worker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS work_job (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    worker_id INTEGER NOT NULL REFERENCES work_worker(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS work_steal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    job_id INTEGER NOT NULL REFERENCES work_job(id),
    from_worker_id INTEGER NOT NULL REFERENCES work_worker(id),
    to_worker_id INTEGER NOT NULL REFERENCES work_worker(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS work_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    job_id INTEGER REFERENCES work_job(id),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS work_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    waiting INTEGER NOT NULL CHECK (waiting >= 0),
    held INTEGER NOT NULL CHECK (held >= 0),
    active INTEGER NOT NULL CHECK (active >= 0),
    needed INTEGER NOT NULL CHECK (needed >= 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS work_scale (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    direction TEXT NOT NULL CHECK (direction IN ('fill', 'up', 'down')),
    worker_id INTEGER NOT NULL REFERENCES work_worker(id),
    job_id INTEGER REFERENCES work_job(id),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS work_release (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    worker_id INTEGER NOT NULL UNIQUE REFERENCES work_worker(id),
    scale_id INTEGER NOT NULL REFERENCES work_scale(id),
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schedule_tenant (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    quota INTEGER NOT NULL CHECK (quota > 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS schedule_turn (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    tenant_id INTEGER NOT NULL REFERENCES schedule_tenant(id),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS priority_work (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    rank INTEGER NOT NULL CHECK (rank IN (1, 2, 3)),
    age INTEGER NOT NULL CHECK (age >= 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS priority_serve (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    work_id INTEGER NOT NULL REFERENCES priority_work(id),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS slo_objective (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    deadline TEXT NOT NULL CHECK (length(trim(deadline)) > 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS slo_service (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    objective_id INTEGER NOT NULL REFERENCES slo_objective(id),
    result TEXT NOT NULL CHECK (result IN ('met', 'missed')),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS path_step (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    length INTEGER NOT NULL CHECK (length IN (1, 2)),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS path_link (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    step_id INTEGER NOT NULL UNIQUE REFERENCES path_step(id),
    predecessor_id INTEGER NOT NULL REFERENCES path_step(id),
    recorded_at TEXT NOT NULL,
    CHECK (step_id != predecessor_id)
);

CREATE TABLE IF NOT EXISTS path_deadline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL UNIQUE REFERENCES task(id),
    deadline TEXT NOT NULL CHECK (length(trim(deadline)) > 0),
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS opt_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    length INTEGER NOT NULL CHECK (length IN (1, 2)),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS opt_constraint (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    activity_id INTEGER NOT NULL REFERENCES opt_activity(id),
    after_id INTEGER NOT NULL REFERENCES opt_activity(id),
    recorded_at TEXT NOT NULL,
    UNIQUE (activity_id, after_id),
    CHECK (activity_id != after_id)
);

CREATE TABLE IF NOT EXISTS opt_capacity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL UNIQUE REFERENCES task(id),
    capacity INTEGER NOT NULL CHECK (capacity IN (1, 2)),
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS opt_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL UNIQUE REFERENCES task(id),
    finish INTEGER NOT NULL CHECK (finish >= 0),
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS opt_placement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL REFERENCES opt_plan(id),
    activity_id INTEGER NOT NULL REFERENCES opt_activity(id),
    start INTEGER NOT NULL CHECK (start >= 0),
    UNIQUE (plan_id, activity_id)
);

CREATE TABLE IF NOT EXISTS learn_outcome (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    kind TEXT NOT NULL CHECK (length(trim(kind)) > 0),
    length INTEGER NOT NULL CHECK (length IN (1, 2)),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS learn_forecast (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    kind TEXT NOT NULL CHECK (length(trim(kind)) > 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS learn_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL UNIQUE REFERENCES task(id),
    finish INTEGER NOT NULL CHECK (finish >= 0),
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS learn_placement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL REFERENCES learn_plan(id),
    forecast_id INTEGER NOT NULL REFERENCES learn_forecast(id),
    predicted INTEGER NOT NULL CHECK (predicted IN (1, 2)),
    start INTEGER NOT NULL CHECK (start >= 0),
    UNIQUE (plan_id, forecast_id)
);

CREATE TABLE IF NOT EXISTS bandit_action (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS bandit_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS bandit_trial (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    context_id INTEGER NOT NULL REFERENCES bandit_context(id),
    action_id INTEGER NOT NULL REFERENCES bandit_action(id),
    reward INTEGER NOT NULL CHECK (reward IN (1, 2)),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS bandit_choice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL UNIQUE REFERENCES task(id),
    context_id INTEGER NOT NULL REFERENCES bandit_context(id),
    action_id INTEGER NOT NULL REFERENCES bandit_action(id),
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eval_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    state TEXT NOT NULL CHECK (length(trim(state)) > 0),
    action TEXT NOT NULL CHECK (length(trim(action)) > 0),
    reward INTEGER NOT NULL CHECK (reward IN (1, 2)),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS eval_rule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    state TEXT NOT NULL CHECK (length(trim(state)) > 0),
    action TEXT NOT NULL CHECK (length(trim(action)) > 0),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, state)
);

CREATE TABLE IF NOT EXISTS eval_score (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL UNIQUE REFERENCES task(id),
    total INTEGER NOT NULL CHECK (total >= 0),
    count INTEGER NOT NULL CHECK (count >= 1),
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS safe_action (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    risk INTEGER NOT NULL CHECK (risk IN (1, 2)),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS safe_probe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    state TEXT NOT NULL CHECK (length(trim(state)) > 0),
    action_id INTEGER NOT NULL REFERENCES safe_action(id),
    reward INTEGER NOT NULL CHECK (reward IN (1, 2)),
    recorded_at TEXT NOT NULL,
    UNIQUE (task_id, name)
);

CREATE TABLE IF NOT EXISTS safe_effect (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL UNIQUE REFERENCES task(id),
    state TEXT NOT NULL CHECK (length(trim(state)) > 0),
    action TEXT NOT NULL CHECK (length(trim(action)) > 0),
    instead TEXT NOT NULL CHECK (length(trim(instead)) > 0),
    effect INTEGER NOT NULL CHECK (effect IN (-1, 0, 1)),
    recorded_at TEXT NOT NULL,
    CHECK (action != instead)
);
