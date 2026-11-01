-- 07 · Small "dashboard" style reports

-- Genre popularity as a share of all loans
SELECT b.genre,
       COUNT(*) AS loans,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM loans), 1) AS pct
FROM loans l JOIN books b ON b.book_id = l.book_id
GROUP BY b.genre
ORDER BY loans DESC;

-- Student vs staff borrowing habits
SELECT m.kind,
       COUNT(DISTINCT m.member_id) AS members,
       COUNT(l.loan_id) AS loans,
       ROUND(1.0 * COUNT(l.loan_id) / COUNT(DISTINCT m.member_id), 1) AS loans_per_member
FROM members m LEFT JOIN loans l ON l.member_id = m.member_id
GROUP BY m.kind;

-- Most-read authors (counting every author of co-written books)
SELECT a.name, COUNT(*) AS loans
FROM loans l
JOIN book_authors ba ON ba.book_id = l.book_id
JOIN authors a ON a.author_id = ba.author_id
GROUP BY a.author_id
ORDER BY loans DESC, a.name
LIMIT 5;
