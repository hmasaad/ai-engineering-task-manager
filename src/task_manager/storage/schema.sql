PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS workspace (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    engineer_name TEXT NOT NULL CHECK (length(trim(engineer_name)) > 0)
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
