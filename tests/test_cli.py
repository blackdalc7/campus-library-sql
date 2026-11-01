from library.cli import main, table


def run(capsys, *args, db=":memory:"):
    code = main(["--db", str(db), "--today", "2026-10-30", *args])
    out = capsys.readouterr()
    return code, out.out, out.err


def test_search(capsys):
    code, out, _ = run(capsys, "search", "asimov")
    assert code == 0
    assert "Foundation" in out and "I, Robot" in out


def test_borrow_then_return_persists(capsys, tmp_path):
    path = tmp_path / "lib.db"
    assert run(capsys, "borrow", "3", "4", db=path)[1].startswith("loan #")
    assert "on time" in run(capsys, "return", "3", "4", db=path)[1]


def test_errors_exit_nonzero(capsys):
    code, _, err = run(capsys, "borrow", "2", "4")
    assert code == 1
    assert "no copies available" in err


def test_overdue_history_popular_stats(capsys):
    assert "6.00" in run(capsys, "overdue")[1]
    assert "Python Crash Course" in run(capsys, "history", "2")[1]
    assert "Introduction to Algorithms" in run(capsys, "popular", "-n", "1")[1]
    assert "on_loan_now" in run(capsys, "stats")[1]


def test_sql_command(capsys):
    code, out, _ = run(capsys, "sql", "sql/queries/05_cte_and_windows.sql")
    assert code == 0
    assert "running_total" in out


def test_table_helper():
    assert table([]) == "(no rows)"
    text = table([{"a": 1, "b": None}])
    assert text.splitlines() == ["a  b", "-  -", "1"]
