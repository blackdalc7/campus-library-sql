-- 06 · Views and triggers defined in schema.sql

-- Availability view: copies minus open loans
SELECT title, copies, available
FROM book_availability
WHERE available < copies
ORDER BY available, title;

-- Late returns with fines (computed on returned loans only, so the answer doesn't change
-- with today's date). The `fines` view also includes books that are still out.
SELECT m.name, b.title, f.days_late, printf('%.2f', f.fine) AS fine
FROM fines f
JOIN loans l   ON l.loan_id = f.loan_id
JOIN members m ON m.member_id = f.member_id
JOIN books b   ON b.book_id = f.book_id
WHERE l.returned_on IS NOT NULL
ORDER BY f.fine DESC;

-- Uncomment to see the trigger stop a loan when no copies are left
-- ("The Left Hand of Darkness" has 1 copy and it is already out):
-- INSERT INTO loans (book_id, member_id, loaned_on, due_on) VALUES (2, 4, '2026-10-28', '2026-11-18');
