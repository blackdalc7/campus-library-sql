"""All the library operations. Every query uses ? placeholders (never string formatting),
so user input can't change the SQL."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, timedelta

LOAN_DAYS = 21
FINE_PER_DAY = 0.25
FINE_CAP = 10.0


class LibraryError(Exception):
    """A rule was broken (no copies left, loan limit, unknown id...)."""


@dataclass(frozen=True)
class Overdue:
    member: str
    email: str
    title: str
    due_on: str
    days_late: int

    @property
    def fine(self) -> float:
        return min(FINE_CAP, self.days_late * FINE_PER_DAY)


def search(conn: sqlite3.Connection, text: str) -> list[sqlite3.Row]:
    """Search titles, authors and genres."""
    like = f"%{text}%"
    return conn.execute(
        """
        SELECT b.book_id, b.title, GROUP_CONCAT(a.name, ', ') AS authors, b.genre, b.year,
               v.available, b.copies
        FROM books b
        JOIN book_authors ba ON ba.book_id = b.book_id
        JOIN authors a ON a.author_id = ba.author_id
        JOIN book_availability v ON v.book_id = b.book_id
        WHERE b.book_id IN (
            SELECT b2.book_id FROM books b2
            JOIN book_authors ba2 ON ba2.book_id = b2.book_id
            JOIN authors a2 ON a2.author_id = ba2.author_id
            WHERE b2.title LIKE ? OR a2.name LIKE ? OR b2.genre LIKE ?
        )
        GROUP BY b.book_id
        ORDER BY b.title
        """,
        (like, like, like),
    ).fetchall()


def borrow(conn: sqlite3.Connection, book_id: int, member_id: int, today: date) -> int:
    """Create a loan. The database triggers enforce copies and loan limits."""
    if not conn.execute("SELECT 1 FROM members WHERE member_id = ?", (member_id,)).fetchone():
        raise LibraryError(f"no member with id {member_id}")
    if not conn.execute("SELECT 1 FROM books WHERE book_id = ?", (book_id,)).fetchone():
        raise LibraryError(f"no book with id {book_id}")
    due = today + timedelta(days=LOAN_DAYS)
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO loans (book_id, member_id, loaned_on, due_on) VALUES (?, ?, ?, ?)",
                (book_id, member_id, today.isoformat(), due.isoformat()),
            )
    except sqlite3.IntegrityError as exc:  # raised by RAISE(ABORT, ...) in the triggers
        raise LibraryError(str(exc)) from None
    return int(cur.lastrowid)


def return_book(conn: sqlite3.Connection, book_id: int, member_id: int, today: date) -> float:
    """Close the open loan and return the fine owed (0 if on time)."""
    row = conn.execute(
        "SELECT loan_id, due_on FROM loans "
        "WHERE book_id = ? AND member_id = ? AND returned_on IS NULL",
        (book_id, member_id),
    ).fetchone()
    if row is None:
        raise LibraryError("that member doesn't have that book")
    with conn:
        conn.execute(
            "UPDATE loans SET returned_on = ? WHERE loan_id = ?", (today.isoformat(), row["loan_id"])
        )
    days_late = (today - date.fromisoformat(row["due_on"])).days
    return min(FINE_CAP, max(0, days_late) * FINE_PER_DAY)


def overdue(conn: sqlite3.Connection, today: date) -> list[Overdue]:
    rows = conn.execute(
        """
        SELECT m.name, m.email, b.title, l.due_on,
               CAST(julianday(?) - julianday(l.due_on) AS INTEGER) AS days_late
        FROM loans l
        JOIN members m ON m.member_id = l.member_id
        JOIN books b ON b.book_id = l.book_id
        WHERE l.returned_on IS NULL AND l.due_on < ?
        ORDER BY days_late DESC, m.name
        """,
        (today.isoformat(), today.isoformat()),
    ).fetchall()
    return [Overdue(*row) for row in rows]


def member_history(conn: sqlite3.Connection, member_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT b.title, l.loaned_on, l.due_on, l.returned_on
        FROM loans l JOIN books b ON b.book_id = l.book_id
        WHERE l.member_id = ?
        ORDER BY l.loaned_on DESC
        """,
        (member_id,),
    ).fetchall()


def popular(conn: sqlite3.Connection, limit: int = 5) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT b.title, COUNT(*) AS times_borrowed
        FROM loans l JOIN books b ON b.book_id = l.book_id
        GROUP BY b.book_id
        ORDER BY times_borrowed DESC, b.title
        LIMIT ?
        """,
        (limit,),
    ).fetchall()


def stats(conn: sqlite3.Connection) -> dict[str, int]:
    one = lambda sql: conn.execute(sql).fetchone()[0]  # noqa: E731
    return {
        "titles": one("SELECT COUNT(*) FROM books"),
        "copies": one("SELECT SUM(copies) FROM books"),
        "authors": one("SELECT COUNT(*) FROM authors"),
        "members": one("SELECT COUNT(*) FROM members"),
        "loans_all_time": one("SELECT COUNT(*) FROM loans"),
        "on_loan_now": one("SELECT COUNT(*) FROM loans WHERE returned_on IS NULL"),
    }
