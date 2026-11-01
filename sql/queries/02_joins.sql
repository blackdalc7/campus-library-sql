-- 02 · Joins: INNER JOIN, LEFT JOIN, many-to-many

-- Every book with its author(s). GROUP_CONCAT merges co-authors into one line.
SELECT b.title, GROUP_CONCAT(a.name, ', ') AS authors
FROM books b
JOIN book_authors ba ON ba.book_id = b.book_id
JOIN authors a       ON a.author_id = ba.author_id
GROUP BY b.book_id
ORDER BY b.title;

-- Who has what right now
SELECT m.name, b.title, l.due_on
FROM loans l
JOIN members m ON m.member_id = l.member_id
JOIN books b   ON b.book_id   = l.book_id
WHERE l.returned_on IS NULL
ORDER BY l.due_on;

-- Books that have NEVER been borrowed (LEFT JOIN + IS NULL)
SELECT b.title
FROM books b
LEFT JOIN loans l ON l.book_id = b.book_id
WHERE l.loan_id IS NULL
ORDER BY b.title;
