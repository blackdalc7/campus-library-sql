-- 05 · CTEs and window functions (SQLite 3.25+)

-- Rank books inside each genre by popularity
WITH counts AS (
    SELECT b.genre, b.title, COUNT(l.loan_id) AS borrowed
    FROM books b LEFT JOIN loans l ON l.book_id = b.book_id
    GROUP BY b.book_id
)
SELECT genre, title, borrowed,
       RANK() OVER (PARTITION BY genre ORDER BY borrowed DESC) AS rank_in_genre
FROM counts
WHERE borrowed > 0
ORDER BY genre, rank_in_genre;

-- Loans per month with a running total
WITH monthly AS (
    SELECT strftime('%Y-%m', loaned_on) AS month, COUNT(*) AS loans
    FROM loans GROUP BY month
)
SELECT month, loans, SUM(loans) OVER (ORDER BY month) AS running_total
FROM monthly
ORDER BY month;

-- Each member's previous book (LAG) to see reading "journeys"
SELECT m.name, b.title,
       LAG(b.title) OVER (PARTITION BY m.member_id ORDER BY l.loaned_on) AS previous_book
FROM loans l
JOIN members m ON m.member_id = l.member_id
JOIN books b ON b.book_id = l.book_id
WHERE m.member_id IN (1, 2, 3)
ORDER BY m.name, l.loaned_on;
