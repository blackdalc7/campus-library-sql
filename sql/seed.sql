-- Sample data. Books and authors are real; members and loans are made up.
-- Loan dates are fixed in 2026 so the example queries give stable answers.

INSERT INTO authors (author_id, name, country) VALUES
 (1, 'Frank Herbert', 'USA'), (2, 'Ursula K. Le Guin', 'USA'), (3, 'Isaac Asimov', 'USA'),
 (4, 'Mary Shelley', 'UK'), (5, 'George Orwell', 'UK'), (6, 'Jane Austen', 'UK'),
 (7, 'Chinua Achebe', 'Nigeria'), (8, 'Gabriel García Márquez', 'Colombia'),
 (9, 'Haruki Murakami', 'Japan'), (10, 'Thomas H. Cormen', 'USA'),
 (11, 'Charles E. Leiserson', 'USA'), (12, 'Ronald L. Rivest', 'USA'),
 (13, 'Clifford Stein', 'USA'), (14, 'Brian W. Kernighan', 'Canada'),
 (15, 'Dennis M. Ritchie', 'USA'), (16, 'Andrew S. Tanenbaum', 'USA'),
 (17, 'Yuval Noah Harari', 'Israel'), (18, 'Carl Sagan', 'USA'),
 (19, 'Stephen Hawking', 'UK'), (20, 'Chimamanda Ngozi Adichie', 'Nigeria'),
 (21, 'Terry Pratchett', 'UK'), (22, 'Neil Gaiman', 'UK'), (23, 'Al Sweigart', 'USA'),
 (24, 'Eric Matthes', 'USA'), (25, 'Abraham Silberschatz', 'USA');

INSERT INTO books (book_id, isbn, title, genre, year, copies) VALUES
 (1, '9780441013593', 'Dune', 'Science Fiction', 1965, 3),
 (2, '9780441478125', 'The Left Hand of Darkness', 'Science Fiction', 1969, 1),
 (3, '9780553293357', 'Foundation', 'Science Fiction', 1951, 2),
 (4, '9780553382563', 'I, Robot', 'Science Fiction', 1950, 1),
 (5, '9780486282114', 'Frankenstein', 'Classic', 1818, 2),
 (6, '9780451524935', '1984', 'Classic', 1949, 3),
 (7, '9780451526342', 'Animal Farm', 'Classic', 1945, 2),
 (8, '9780141439518', 'Pride and Prejudice', 'Classic', 1813, 2),
 (9, '9780385474542', 'Things Fall Apart', 'Literary Fiction', 1958, 2),
 (10, '9780060883287', 'One Hundred Years of Solitude', 'Literary Fiction', 1967, 1),
 (11, '9780307476463', 'Norwegian Wood', 'Literary Fiction', 1987, 1),
 (12, '9780262046305', 'Introduction to Algorithms', 'Computer Science', 2022, 4),
 (13, '9780131103627', 'The C Programming Language', 'Computer Science', 1988, 2),
 (14, '9780133591620', 'Modern Operating Systems', 'Computer Science', 2014, 2),
 (15, '9780062316097', 'Sapiens', 'Non-fiction', 2011, 2),
 (16, '9780345539434', 'Cosmos', 'Non-fiction', 1980, 1),
 (17, '9780553380163', 'A Brief History of Time', 'Non-fiction', 1988, 2),
 (18, '9780307455925', 'Americanah', 'Literary Fiction', 2013, 1),
 (19, '9780060853983', 'Good Omens', 'Fantasy', 1990, 2),
 (20, '9780552166591', 'The Colour of Magic', 'Fantasy', 1983, 1),
 (21, '9780062255655', 'The Ocean at the End of the Lane', 'Fantasy', 2013, 1),
 (22, '9781593279929', 'Automate the Boring Stuff with Python', 'Computer Science', 2019, 3),
 (23, '9781718502703', 'Python Crash Course', 'Computer Science', 2023, 3),
 (24, '9781119800361', 'Operating System Concepts', 'Computer Science', 2021, 2),
 (25, '9780547928227', 'A Wizard of Earthsea', 'Fantasy', 1968, 1);

INSERT INTO book_authors (book_id, author_id) VALUES
 (1, 1), (2, 2), (3, 3), (4, 3), (5, 4), (6, 5), (7, 5), (8, 6), (9, 7), (10, 8),
 (11, 9), (12, 10), (12, 11), (12, 12), (12, 13), (13, 14), (13, 15), (14, 16),
 (15, 17), (16, 18), (17, 19), (18, 20), (19, 21), (19, 22), (20, 21), (21, 22),
 (22, 23), (23, 24), (24, 25), (25, 2);

INSERT INTO members (member_id, name, email, kind, joined_on) VALUES
 (1, 'Aisha Khan', 'aisha.khan@uni.example', 'student', '2025-09-01'),
 (2, 'Ben Carter', 'ben.carter@uni.example', 'student', '2025-09-01'),
 (3, 'Chloe Nguyen', 'chloe.nguyen@uni.example', 'student', '2025-09-03'),
 (4, 'Diego Alvarez', 'diego.alvarez@uni.example', 'student', '2025-09-10'),
 (5, 'Emma Schmidt', 'emma.schmidt@uni.example', 'student', '2026-01-15'),
 (6, 'Farah Haddad', 'farah.haddad@uni.example', 'student', '2026-01-15'),
 (7, 'George Okafor', 'george.okafor@uni.example', 'student', '2026-02-02'),
 (8, 'Hana Sato', 'hana.sato@uni.example', 'student', '2026-02-20'),
 (9, 'Ivan Petrov', 'ivan.petrov@uni.example', 'student', '2026-03-05'),
 (10, 'Julia Rossi', 'julia.rossi@uni.example', 'student', '2026-09-01'),
 (11, 'Dr. Kofi Mensah', 'k.mensah@uni.example', 'staff', '2020-01-06'),
 (12, 'Prof. Laura Chen', 'l.chen@uni.example', 'staff', '2018-08-20');

-- returned loans (history)
INSERT INTO loans (book_id, member_id, loaned_on, due_on, returned_on) VALUES
 (1, 1, '2026-01-10', '2026-01-31', '2026-01-28'),
 (12, 1, '2026-02-01', '2026-02-22', '2026-02-20'),
 (6, 2, '2026-01-12', '2026-02-02', '2026-02-10'),
 (23, 2, '2026-02-15', '2026-03-08', '2026-03-01'),
 (22, 3, '2026-02-02', '2026-02-23', '2026-02-23'),
 (1, 3, '2026-03-01', '2026-03-22', '2026-04-05'),
 (12, 4, '2026-03-03', '2026-03-24', '2026-03-20'),
 (13, 4, '2026-03-03', '2026-03-24', '2026-04-30'),
 (15, 5, '2026-03-10', '2026-03-31', '2026-03-29'),
 (17, 5, '2026-04-02', '2026-04-23', '2026-04-22'),
 (19, 6, '2026-04-05', '2026-04-26', '2026-04-26'),
 (1, 6, '2026-04-10', '2026-05-01', '2026-04-30'),
 (6, 7, '2026-04-12', '2026-05-03', '2026-05-20'),
 (9, 7, '2026-05-01', '2026-05-22', '2026-05-21'),
 (12, 8, '2026-05-02', '2026-05-23', '2026-05-23'),
 (14, 8, '2026-05-02', '2026-05-23', '2026-06-01'),
 (23, 9, '2026-05-10', '2026-05-31', '2026-05-30'),
 (1, 11, '2026-05-12', '2026-06-02', '2026-06-01'),
 (24, 11, '2026-05-12', '2026-06-02', '2026-06-20'),
 (16, 12, '2026-06-01', '2026-06-22', '2026-06-15'),
 (6, 1, '2026-06-03', '2026-06-24', '2026-06-24'),
 (22, 2, '2026-06-05', '2026-06-26', '2026-06-25'),
 (12, 3, '2026-09-08', '2026-09-29', '2026-09-28'),
 (10, 4, '2026-09-08', '2026-09-29', '2026-10-15'),
 (23, 10, '2026-09-10', '2026-10-01', '2026-09-30');

-- still out (some overdue relative to late October 2026)
INSERT INTO loans (book_id, member_id, loaned_on, due_on, returned_on) VALUES
 (1, 1, '2026-10-01', '2026-10-22', NULL),
 (12, 2, '2026-10-05', '2026-10-26', NULL),
 (2, 3, '2026-10-20', '2026-11-10', NULL),
 (13, 5, '2026-09-15', '2026-10-06', NULL),
 (6, 6, '2026-10-18', '2026-11-08', NULL),
 (23, 7, '2026-10-21', '2026-11-11', NULL),
 (14, 11, '2026-10-02', '2026-10-23', NULL),
 (12, 12, '2026-10-10', '2026-10-31', NULL),
 (25, 9, '2026-10-25', '2026-11-15', NULL);
