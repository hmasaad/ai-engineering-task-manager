"""Named workers and the pending jobs they hold."""

import sqlite3


def workers(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, task_id, name, recorded_at
        FROM work_worker
        WHERE task_id = ?
        ORDER BY id ASC
        """,
        (task_id,),
    ).fetchall()


def worker_by_name(connection: sqlite3.Connection, task_id: int, name: str) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, name, recorded_at
        FROM work_worker
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def insert_worker(
    connection: sqlite3.Connection, task_id: int, name: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO work_worker (task_id, name, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, name, recorded_at),
    )


def jobs(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, task_id, worker_id, name, recorded_at
        FROM work_job
        WHERE task_id = ?
        ORDER BY id ASC
        """,
        (task_id,),
    ).fetchall()


def job_by_name(connection: sqlite3.Connection, task_id: int, name: str) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, worker_id, name, recorded_at
        FROM work_job
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def insert_job(
    connection: sqlite3.Connection,
    task_id: int,
    worker_id: int,
    name: str,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO work_job (task_id, worker_id, name, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, worker_id, name, recorded_at),
    )


def oldest_job(connection: sqlite3.Connection, worker_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, worker_id, name, recorded_at
        FROM work_job
        WHERE worker_id = ?
        ORDER BY id ASC
        LIMIT 1
        """,
        (worker_id,),
    ).fetchone()


def move_job(connection: sqlite3.Connection, job_id: int, worker_id: int) -> None:
    connection.execute(
        "UPDATE work_job SET worker_id = ? WHERE id = ?",
        (worker_id, job_id),
    )


def steals(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT work_steal.name AS name,
               work_job.name AS job,
               source.name AS from_worker,
               target.name AS to_worker
        FROM work_steal
        JOIN work_job ON work_job.id = work_steal.job_id
        JOIN work_worker AS source ON source.id = work_steal.from_worker_id
        JOIN work_worker AS target ON target.id = work_steal.to_worker_id
        WHERE work_steal.task_id = ?
        ORDER BY work_steal.id ASC
        """,
        (task_id,),
    ).fetchall()


def steal_by_name(connection: sqlite3.Connection, task_id: int, name: str) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, job_id, from_worker_id, to_worker_id, name, recorded_at
        FROM work_steal
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def insert_steal(
    connection: sqlite3.Connection,
    task_id: int,
    job_id: int,
    from_worker_id: int,
    to_worker_id: int,
    name: str,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO work_steal (
            task_id, job_id, from_worker_id, to_worker_id, name, recorded_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (task_id, job_id, from_worker_id, to_worker_id, name, recorded_at),
    )


def active_workers(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, task_id, name, recorded_at
        FROM work_worker
        WHERE task_id = ?
          AND id NOT IN (SELECT worker_id FROM work_release)
        ORDER BY id ASC
        """,
        (task_id,),
    ).fetchall()


def is_released(connection: sqlite3.Connection, worker_id: int) -> bool:
    row = connection.execute(
        "SELECT id FROM work_release WHERE worker_id = ?",
        (worker_id,),
    ).fetchone()
    return row is not None


def queue_by_name(connection: sqlite3.Connection, task_id: int, name: str) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, name, job_id, recorded_at
        FROM work_queue
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def insert_queue(
    connection: sqlite3.Connection, task_id: int, name: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO work_queue (task_id, name, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, name, recorded_at),
    )


def waiting(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name
        FROM work_queue
        WHERE task_id = ? AND job_id IS NULL
        ORDER BY id ASC
        """,
        (task_id,),
    ).fetchall()


def oldest_waiting(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, name
        FROM work_queue
        WHERE task_id = ? AND job_id IS NULL
        ORDER BY id ASC
        LIMIT 1
        """,
        (task_id,),
    ).fetchone()


def mark_queued(connection: sqlite3.Connection, queue_id: int, job_id: int) -> None:
    connection.execute(
        "UPDATE work_queue SET job_id = ? WHERE id = ?",
        (job_id, queue_id),
    )


def plan_by_name(connection: sqlite3.Connection, task_id: int, name: str) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, name, waiting, held, active, needed
        FROM work_plan
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def insert_plan(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    waiting_count: int,
    held_count: int,
    active_count: int,
    needed_count: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO work_plan (task_id, name, waiting, held, active, needed, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (task_id, name, waiting_count, held_count, active_count, needed_count, recorded_at),
    )


def plans(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT name, waiting, held, active, needed
        FROM work_plan
        WHERE task_id = ?
        ORDER BY id ASC
        """,
        (task_id,),
    ).fetchall()


def scale_by_name(connection: sqlite3.Connection, task_id: int, name: str) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT id, name FROM work_scale WHERE task_id = ? AND name = ?",
        (task_id, name),
    ).fetchone()


def insert_scale(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    direction: str,
    worker_id: int,
    job_id: int | None,
    recorded_at: str,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO work_scale (task_id, name, direction, worker_id, job_id, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (task_id, name, direction, worker_id, job_id, recorded_at),
    )
    return int(cursor.lastrowid)


def scales(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT work_scale.name AS name,
               work_scale.direction AS direction,
               work_worker.name AS worker,
               work_job.name AS job
        FROM work_scale
        JOIN work_worker ON work_worker.id = work_scale.worker_id
        LEFT JOIN work_job ON work_job.id = work_scale.job_id
        WHERE work_scale.task_id = ?
        ORDER BY work_scale.id ASC
        """,
        (task_id,),
    ).fetchall()


def insert_release(
    connection: sqlite3.Connection,
    task_id: int,
    worker_id: int,
    scale_id: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO work_release (task_id, worker_id, scale_id, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, worker_id, scale_id, recorded_at),
    )


def released(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT work_worker.name AS name
        FROM work_release
        JOIN work_worker ON work_worker.id = work_release.worker_id
        WHERE work_release.task_id = ?
        ORDER BY work_release.id ASC
        """,
        (task_id,),
    ).fetchall()
