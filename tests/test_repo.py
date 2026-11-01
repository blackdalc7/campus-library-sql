from datetime import date

import pytest

from library import repo

TODAY = date(2026, 10, 30)


def test_search_by_title_author_and_genre(conn):
    assert [r["title"] for r in repo.search(conn, "dune")] == ["Dune"]
    assert {r["title"] for r in repo.search(conn, "Orwell")} == {"1984", "Animal Farm"}
    assert len(repo.search(conn, "Fantasy")) == 4


def test_search_shows_all_coauthors(conn):
    (row,) = repo.search(conn, "Gaiman")[:1]
    assert row["title"] == "Good Omens"
    assert row["authors"] == "Terry Pratchett, Neil Gaiman"


def test_search_is_injection_safe(conn):
    assert repo.search(conn, "'; DROP TABLE books; --") == []
    assert conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 25


def test_borrow_and_return_on_time(conn):
    loan = repo.borrow(conn, 3, 4, TODAY)
    row = conn.execute("SELECT due_on FROM loans WHERE loan_id = ?", (loan,)).fetchone()
    assert row["due_on"] == "2026-11-20"
    assert repo.return_book(conn, 3, 4, date(2026, 11, 5)) == 0


def test_late_return_fine_and_cap(conn):
    repo.borrow(conn, 3, 4, TODAY)
    assert repo.return_book(conn, 3, 4, date(2026, 11, 24)) == 1.0  # 4 days late
    repo.borrow(conn, 3, 4, TODAY)
    assert repo.return_book(conn, 3, 4, date(2027, 6, 1)) == repo.FINE_CAP


def test_borrow_errors(conn):
    with pytest.raises(repo.LibraryError, match="no member"):
        repo.borrow(conn, 1, 999, TODAY)
    with pytest.raises(repo.LibraryError, match="no book"):
        repo.borrow(conn, 999, 1, TODAY)
    with pytest.raises(repo.LibraryError, match="no copies"):
        repo.borrow(conn, 2, 4, TODAY)


def test_return_without_loan(conn):
    with pytest.raises(repo.LibraryError):
        repo.return_book(conn, 5, 5, TODAY)


def test_overdue(conn):
    items = repo.overdue(conn, TODAY)
    assert [o.title for o in items] == [
        "The C Programming Language",
        "Dune",
        "Modern Operating Systems",
        "Introduction to Algorithms",
    ]
    assert items[0].days_late == 24
    assert items[0].fine == 6.0


def test_member_history_newest_first(conn):
    titles = [r["title"] for r in repo.member_history(conn, 1)]
    assert titles == ["Dune", "1984", "Introduction to Algorithms", "Dune"]


def test_popular_and_stats(conn):
    top = repo.popular(conn, 2)
    assert [(r["title"], r["times_borrowed"]) for r in top] == [
        ("Introduction to Algorithms", 6),
        ("Dune", 5),
    ]
    s = repo.stats(conn)
    assert s["titles"] == 25
    assert s["on_loan_now"] == 9
