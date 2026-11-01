-- Campus Library schema (SQLite)
-- Run: sqlite3 library.db < sql/schema.sql

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS authors (
    author_id   INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    country     TEXT
);

CREATE TABLE IF NOT EXISTS books (
    book_id     INTEGER PRIMARY KEY,
    isbn        TEXT    NOT NULL UNIQUE,
    title       TEXT    NOT NULL,
    genre       TEXT    NOT NULL,
    year        INTEGER CHECK (year BETWEEN 1400 AND 2100),
    copies      INTEGER NOT NULL DEFAULT 1 CHECK (copies >= 0)
);

-- many-to-many: a book can have several authors
CREATE TABLE IF NOT EXISTS book_authors (
    book_id     INTEGER NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
    author_id   INTEGER NOT NULL REFERENCES authors(author_id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, author_id)
);

CREATE TABLE IF NOT EXISTS members (
    member_id   INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE CHECK (email LIKE '%_@_%._%'),
    kind        TEXT    NOT NULL CHECK (kind IN ('student', 'staff')),
    joined_on   TEXT    NOT NULL DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS loans (
    loan_id     INTEGER PRIMARY KEY,
    book_id     INTEGER NOT NULL REFERENCES books(book_id),
    member_id   INTEGER NOT NULL REFERENCES members(member_id),
    loaned_on   TEXT    NOT NULL,
    due_on      TEXT    NOT NULL,
    returned_on TEXT,
    CHECK (due_on > loaned_on),
    CHECK (returned_on IS NULL OR returned_on >= loaned_on)
);

CREATE INDEX IF NOT EXISTS idx_loans_member ON loans(member_id);
CREATE INDEX IF NOT EXISTS idx_loans_book_open ON loans(book_id) WHERE returned_on IS NULL;
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title COLLATE NOCASE);

-- How many copies of each book are on the shelf right now.
CREATE VIEW IF NOT EXISTS book_availability AS
SELECT b.book_id,
       b.title,
       b.copies,
       b.copies - COUNT(l.loan_id) AS available
FROM books b
LEFT JOIN loans l ON l.book_id = b.book_id AND l.returned_on IS NULL
GROUP BY b.book_id;

-- Fines: 0.25 per day late, capped at 10.00. Unreturned books count up to "today".
CREATE VIEW IF NOT EXISTS fines AS
SELECT l.loan_id,
       l.member_id,
       l.book_id,
       CAST(julianday(COALESCE(l.returned_on, date('now'))) - julianday(l.due_on) AS INTEGER)
           AS days_late,
       MIN(10.0, 0.25 * (julianday(COALESCE(l.returned_on, date('now'))) - julianday(l.due_on)))
           AS fine
FROM loans l
WHERE julianday(COALESCE(l.returned_on, date('now'))) > julianday(l.due_on);

-- Business rule enforced by the database itself: no borrowing when no copies are left.
CREATE TRIGGER IF NOT EXISTS no_loan_without_copy
BEFORE INSERT ON loans
WHEN (SELECT available FROM book_availability WHERE book_id = NEW.book_id) <= 0
BEGIN
    SELECT RAISE(ABORT, 'no copies available');
END;

-- Students can hold at most 3 books at a time, staff 10.
CREATE TRIGGER IF NOT EXISTS loan_limit
BEFORE INSERT ON loans
WHEN (SELECT COUNT(*) FROM loans WHERE member_id = NEW.member_id AND returned_on IS NULL)
     >= (SELECT CASE kind WHEN 'student' THEN 3 ELSE 10 END FROM members
         WHERE member_id = NEW.member_id)
BEGIN
    SELECT RAISE(ABORT, 'loan limit reached');
END;
