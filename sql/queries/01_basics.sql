-- 01 · Basics: SELECT, WHERE, ORDER BY, LIMIT, LIKE

-- All science fiction, oldest first
SELECT title, year
FROM books
WHERE genre = 'Science Fiction'
ORDER BY year;

-- Titles containing "the" (case-insensitive in SQLite for ASCII)
SELECT title FROM books WHERE title LIKE '%the%' ORDER BY title;

-- The 5 newest books
SELECT title, year FROM books ORDER BY year DESC LIMIT 5;

-- Books published in the 1960s
SELECT title, year FROM books WHERE year BETWEEN 1960 AND 1969 ORDER BY year;
