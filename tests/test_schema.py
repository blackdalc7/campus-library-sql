import sqlite3

import pytest

from library import db


def count(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_seed_loaded(conn):
    assert count(conn, "books") == 25
    assert count(conn, "authors") == 25
    assert count(conn, "members") == 12
    assert count(conn, "loans") == 34


def test_foreign_keys_enforced(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO loans (book_id, member_id, loaned_on, due_on) "
            "VALUES (999, 1, '2026-01-01', '2026-01-10')"
        )


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO books (isbn, title, genre, year) VALUES ('9780441013593', 'dupe', 'x', 2000)",
        "INSERT INTO books (isbn, title, genre, year) VALUES ('1', 'future', 'x', 3000)",
        "INSERT INTO books (isbn, title, genre, copies) VALUES ('2', 'neg', 'x', -1)",
        "INSERT INTO members (name, email, kind) VALUES ('x', 'not-an-email', 'student')",
        "INSERT INTO members (name, email, kind) VALUES ('x', 'a@b.co', 'alien')",
        "INSERT INTO loans (book_id, member_id, loaned_on, due_on) "
        "VALUES (3, 10, '2026-02-01', '2026-01-01')",
    ],
)
def test_check_constraints(conn, sql):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(sql)


def test_availability_view(conn):
    row = conn.execute(
        "SELECT copies, available FROM book_availability WHERE title = 'Introduction to Algorithms'"
    ).fetchone()
    assert tuple(row) == (4, 2)


def test_trigger_blocks_loan_with_no_copies(conn):
    # book 2 has one copy and it is out
    with pytest.raises(sqlite3.IntegrityError, match="no copies available"):
        conn.execute(
            "INSERT INTO loans (book_id, member_id, loaned_on, due_on) "
            "VALUES (2, 4, '2026-10-28', '2026-11-18')"
        )


def test_trigger_student_loan_limit(conn):
    for book in (3, 5, 8):
        conn.execute(
            "INSERT INTO loans (book_id, member_id, loaned_on, due_on) "
            "VALUES (?, 10, '2026-10-28', '2026-11-18')",
            (book,),
        )
    with pytest.raises(sqlite3.IntegrityError, match="loan limit"):
        conn.execute(
            "INSERT INTO loans (book_id, member_id, loaned_on, due_on) "
            "VALUES (9, 10, '2026-10-28', '2026-11-18')"
        )


def test_cannot_delete_a_book_that_has_loans(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM books WHERE book_id = 1")


def test_deleting_an_unborrowed_book_cascades_to_book_authors(conn):
    conn.execute("INSERT INTO books (book_id, isbn, title, genre) VALUES (99, 'x', 'New', 'Misc')")
    conn.execute("INSERT INTO book_authors VALUES (99, 1)")
    conn.execute("DELETE FROM books WHERE book_id = 99")
    assert conn.execute("SELECT COUNT(*) FROM book_authors WHERE book_id = 99").fetchone()[0] == 0


def test_open_db_creates_file_once(tmp_path):
    path = tmp_path / "lib.db"
    first = db.open_db(path)
    first.execute("DELETE FROM loans WHERE returned_on IS NOT NULL")
    first.commit()
    first.close()
    again = db.open_db(path)  # must not re-seed
    assert again.execute("SELECT COUNT(*) FROM loans").fetchone()[0] == 9
    again.close()


def test_split_statements_and_describe():
    sql = "-- header\n\n-- first query\nSELECT 1;\n\n-- second\n-- query\nSELECT ';';\n-- trailing\n"
    parts = db.split_statements(sql)
    assert len(parts) == 2
    assert db.describe(parts[0]) == "first query"
    assert db.describe(parts[1]) == "second query"
    assert db.strip_comments(parts[1]) == "SELECT ';';"


@pytest.mark.parametrize("path", sorted((db.SQL_DIR / "queries").glob("*.sql")), ids=lambda p: p.name)
def test_every_example_query_runs(conn, path):
    for statement in db.split_statements(path.read_text(encoding="utf-8")):
        cur = conn.execute(db.strip_comments(statement))
        assert cur.fetchall(), f"query returned nothing: {db.describe(statement)}"
