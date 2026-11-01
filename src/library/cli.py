"""Command line interface.

    python -m library search dune
    python -m library borrow 3 4
    python -m library return 3 4
    python -m library overdue --today 2026-10-30
    python -m library history 1
    python -m library popular
    python -m library stats
    python -m library sql sql/queries/05_cte_and_windows.sql
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from library import db, repo


def table(rows: Sequence[sqlite3.Row] | Sequence[dict], headers: list[str] | None = None) -> str:
    """Format rows as a plain-text table."""
    if not rows:
        return "(no rows)"
    headers = headers or list(rows[0].keys())
    data = [["" if r[h] is None else str(r[h]) for h in headers] for r in rows]
    widths = [max(len(h), *(len(row[i]) for row in data)) for i, h in enumerate(headers)]
    line = "  ".join(h.ljust(w) for h, w in zip(headers, widths, strict=True)).rstrip()
    sep = "  ".join("-" * w for w in widths)
    body = ["  ".join(c.ljust(w) for c, w in zip(row, widths, strict=True)).rstrip() for row in data]
    return "\n".join([line, sep, *body])


def parse_date(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a date (use YYYY-MM-DD): {text}") from None


def run_sql_file(conn: sqlite3.Connection, path: Path) -> str:
    out = []
    for statement in db.split_statements(path.read_text(encoding="utf-8")):
        title = db.describe(statement)
        cur = conn.execute(db.strip_comments(statement))
        rows = cur.fetchall()
        out.append(f"-- {title}" if title else "--")
        if cur.description:
            out.append(table(rows, [d[0] for d in cur.description]))
        out.append("")
    return "\n".join(out)


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="library", description="Campus Library database")
    p.add_argument("--db", default="library.db", help="SQLite file (created on first use)")
    p.add_argument("--today", type=parse_date, default=date.today(), help="pretend today is…")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", help="search titles, authors and genres")
    s.add_argument("text")
    for name in ("borrow", "return"):
        sp = sub.add_parser(name, help=f"{name} a book")
        sp.add_argument("book_id", type=int)
        sp.add_argument("member_id", type=int)
    sub.add_parser("overdue", help="list overdue loans and fines")
    h = sub.add_parser("history", help="a member's loan history")
    h.add_argument("member_id", type=int)
    pop = sub.add_parser("popular", help="most borrowed books")
    pop.add_argument("-n", type=int, default=5)
    sub.add_parser("stats", help="counts")
    q = sub.add_parser("sql", help="run every query in a .sql file and print the results")
    q.add_argument("file", type=Path)
    return p


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    conn = db.open_db(args.db)
    try:
        if args.command == "search":
            print(table(repo.search(conn, args.text),
                        ["book_id", "title", "authors", "year", "available"]))
        elif args.command == "borrow":
            loan = repo.borrow(conn, args.book_id, args.member_id, args.today)
            print(f"loan #{loan} created, due in {repo.LOAN_DAYS} days")
        elif args.command == "return":
            fine = repo.return_book(conn, args.book_id, args.member_id, args.today)
            print(f"returned. fine owed: {fine:.2f}" if fine else "returned on time, thanks!")
        elif args.command == "overdue":
            items = repo.overdue(conn, args.today)
            rows = [{**vars(o), "fine": f"{o.fine:.2f}"} for o in items]
            print(table(rows, ["member", "title", "due_on", "days_late", "fine"]))
        elif args.command == "history":
            print(table(repo.member_history(conn, args.member_id)))
        elif args.command == "popular":
            print(table(repo.popular(conn, args.n)))
        elif args.command == "stats":
            for key, value in repo.stats(conn).items():
                print(f"{key:15} {value}")
        elif args.command == "sql":
            print(run_sql_file(conn, args.file))
    except (repo.LibraryError, sqlite3.Error, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()
    return 0
