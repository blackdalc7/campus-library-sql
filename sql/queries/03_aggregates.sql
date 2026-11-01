-- 03 · Aggregates: COUNT, SUM, AVG, GROUP BY, HAVING

-- How many books and copies per genre
SELECT genre, COUNT(*) AS titles, SUM(copies) AS copies
FROM books
GROUP BY genre
ORDER BY copies DESC;

-- Most borrowed books (all time)
SELECT b.title, COUNT(*) AS times_borrowed
FROM loans l JOIN books b ON b.book_id = l.book_id
GROUP BY b.book_id
ORDER BY times_borrowed DESC, b.title
LIMIT 5;

-- Members who have borrowed 3 or more books (HAVING filters groups, WHERE filters rows)
SELECT m.name, COUNT(*) AS loans
FROM loans l JOIN members m ON m.member_id = l.member_id
GROUP BY m.member_id
HAVING COUNT(*) >= 3
ORDER BY loans DESC;

-- Average loan length in days for returned books, per genre
SELECT b.genre,
       ROUND(AVG(julianday(l.returned_on) - julianday(l.loaned_on)), 1) AS avg_days
FROM loans l JOIN books b ON b.book_id = l.book_id
WHERE l.returned_on IS NOT NULL
GROUP BY b.genre
ORDER BY avg_days DESC;
