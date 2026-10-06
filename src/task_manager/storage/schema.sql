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
