-- 04 · Subqueries: IN, NOT EXISTS, scalar subqueries

-- Members who have borrowed a Classic
SELECT name FROM members
WHERE member_id IN (
    SELECT l.member_id FROM loans l JOIN books b ON b.book_id = l.book_id
    WHERE b.genre = 'Classic'
)
ORDER BY name;

-- Members who have never returned anything late
SELECT m.name FROM members m
WHERE EXISTS (SELECT 1 FROM loans l WHERE l.member_id = m.member_id)
  AND NOT EXISTS (
    SELECT 1 FROM loans l
    WHERE l.member_id = m.member_id AND l.returned_on > l.due_on
)
ORDER BY m.name;

-- Books borrowed more often than the average book
SELECT b.title, (SELECT COUNT(*) FROM loans l WHERE l.book_id = b.book_id) AS borrowed
FROM books b
WHERE (SELECT COUNT(*) FROM loans l WHERE l.book_id = b.book_id) >
      (SELECT AVG(n) FROM (SELECT COUNT(*) AS n FROM loans GROUP BY book_id))
ORDER BY borrowed DESC;
