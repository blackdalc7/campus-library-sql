"""Opening the database, creating the schema and loading the seed data."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SQL_DIR = Path(__file__).resolve().parents[2] / "sql"


def connect(path: str | Path = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init(conn: sqlite3.Connection, seed: bool = True) -> None:
    conn.executescript((SQL_DIR / "schema.sql").read_text(encoding="utf-8"))
    if seed:
        conn.executescript((SQL_DIR / "seed.sql").read_text(encoding="utf-8"))
    conn.commit()


def open_db(path: str | Path) -> sqlite3.Connection:
    """Open a database file, creating and seeding it the first time."""
    is_new = str(path) == ":memory:" or not Path(path).exists()
    conn = connect(path)
    if is_new:
        init(conn)
    return conn


def split_statements(sql: str) -> list[str]:
    """Split a .sql file into statements, keeping the comment just above each one.

    Uses ``sqlite3.complete_statement`` so semicolons inside strings don't confuse it.
    """
    statements, buffer = [], ""
    for line in sql.splitlines(keepends=True):
        buffer += line
        if sqlite3.complete_statement(buffer):
            statements.append(buffer.strip())
            buffer = ""
    return [s for s in statements if strip_comments(s)]


def strip_comments(statement: str) -> str:
    return "\n".join(
        line for line in statement.splitlines() if not line.lstrip().startswith("--")
    ).strip()


def describe(statement: str) -> str:
    """The comment line(s) right above a statement, used as its title."""
    block: list[str] = []
    for line in statement.splitlines():
        if not line.strip():
            block = []  # a blank line ends the previous comment block
            continue
        if not line.lstrip().startswith("--"):
            break
        block.append(line.lstrip("- ").strip())
    return " ".join(block)
