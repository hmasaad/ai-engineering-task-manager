"""Points, nodes, local reports, and one stored agreement."""

import sqlite3


def point_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, name, setting
        FROM consensus_point
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_points(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM consensus_point WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_point(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    setting: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO consensus_point (task_id, name, setting, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, name, setting, recorded_at),
    )


def points(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name, setting
        FROM consensus_point
        WHERE task_id = ?
        ORDER BY id
        """,
        (task_id,),
    ).fetchall()


def node_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, name
        FROM consensus_node
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_nodes(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM consensus_node WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_node(
    connection: sqlite3.Connection, task_id: int, name: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO consensus_node (task_id, name, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, name, recorded_at),
    )


def nodes(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name
        FROM consensus_node
        WHERE task_id = ?
        ORDER BY id
        """,
        (task_id,),
    ).fetchall()


def report_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id
        FROM consensus_report
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def report_for_pair(
    connection: sqlite3.Connection, task_id: int, node_id: int, point_id: int
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id
        FROM consensus_report
        WHERE task_id = ? AND node_id = ? AND point_id = ?
        """,
        (task_id, node_id, point_id),
    ).fetchone()


def count_reports(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM consensus_report WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_report(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    node_id: int,
    point_id: int,
    score: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO consensus_report (
            task_id, name, node_id, point_id, score, recorded_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (task_id, name, node_id, point_id, score, recorded_at),
    )


def reports(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT r.id, r.name, r.node_id, r.point_id, r.score,
               n.name AS node, p.name AS point
        FROM consensus_report r
        JOIN consensus_node n ON n.id = r.node_id
        JOIN consensus_point p ON p.id = r.point_id
        WHERE r.task_id = ?
        ORDER BY r.id
        """,
        (task_id,),
    ).fetchall()


def clear_agreement(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute(
        "DELETE FROM consensus_proposal WHERE task_id = ?", (task_id,)
    )
    connection.execute("DELETE FROM consensus_choice WHERE task_id = ?", (task_id,))


def insert_proposal(
    connection: sqlite3.Connection,
    task_id: int,
    node: str,
    point: str,
    position: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO consensus_proposal (task_id, node, point, position, recorded_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (task_id, node, point, position, recorded_at),
    )


def proposals(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT node, point
        FROM consensus_proposal
        WHERE task_id = ?
        ORDER BY position, id
        """,
        (task_id,),
    ).fetchall()


def insert_choice(
    connection: sqlite3.Connection,
    task_id: int,
    point: str,
    node: str,
    suggestions: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO consensus_choice (
            task_id, point, node, suggestions, recorded_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (task_id, point, node, suggestions, recorded_at),
    )


def choice_for(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT point, node, suggestions
        FROM consensus_choice
        WHERE task_id = ?
        """,
        (task_id,),
    ).fetchone()
