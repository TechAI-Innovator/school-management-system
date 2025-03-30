-- -- SQLite does not support CREATE DATABASE

-- -- Create 'roles' table
-- CREATE TABLE IF NOT EXISTS roles (
--     role_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     role_name TEXT UNIQUE NOT NULL
-- );

-- -- Create 'classes' table
-- CREATE TABLE IF NOT EXISTS classes (
--     class_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     class_name TEXT NOT NULL UNIQUE
-- );

-- -- Create 'class_codes' table
-- CREATE TABLE IF NOT EXISTS class_codes (
--     code_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     class_id INTEGER NULL,
--     code TEXT NOT NULL UNIQUE,
--     is_used INTEGER CHECK (is_used IN (0,1)) NOT NULL DEFAULT 0,
--     created_at TEXT DEFAULT CURRENT_TIMESTAMP,
--     updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE SET NULL
-- );

-- -- Create 'subjects' table
-- CREATE TABLE IF NOT EXISTS subjects (
--     subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     subject_name TEXT NOT NULL UNIQUE
-- );

-- -- Create 'students' table
-- CREATE TABLE IF NOT EXISTS students (
--     student_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     surname TEXT NOT NULL,
--     first_name TEXT NOT NULL,
--     middle_name TEXT,
--     username TEXT UNIQUE NOT NULL,
--     password TEXT NOT NULL,
--     phone_number TEXT,
--     email TEXT,
--     date_of_birth TEXT,
--     address TEXT,
--     class_id INTEGER,
--     role_id INTEGER,
--     FOREIGN KEY (class_id) REFERENCES classes(class_id),
--     FOREIGN KEY (role_id) REFERENCES roles(role_id)
-- );

-- -- Create 'staff' table
-- CREATE TABLE IF NOT EXISTS staff (
--     staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     surname TEXT NOT NULL,
--     first_name TEXT NOT NULL,
--     middle_name TEXT,
--     username TEXT UNIQUE,
--     password TEXT,
--     phone_number TEXT,
--     email TEXT,
--     date_of_birth TEXT,
--     address TEXT,
--     role_id INTEGER,
--     is_admin INTEGER CHECK (is_admin IN (0,1)) DEFAULT 0,
--     verification_code TEXT,
--     code_used INTEGER CHECK (code_used IN (0,1)) DEFAULT 0,
--     FOREIGN KEY (role_id) REFERENCES roles(role_id)
-- );

-- -- Create 'terms' table
-- CREATE TABLE IF NOT EXISTS terms (
--     term_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     term TEXT NOT NULL,
--     year INTEGER NOT NULL,
--     start_date TEXT,
--     end_date TEXT,
--     vacation_date TEXT,
--     resumption_date TEXT,
--     is_current INTEGER CHECK (is_current IN (0,1)) DEFAULT 0,
--     status TEXT CHECK (status IN ('Upcoming', 'Active', 'Ended', 'Vacation')) DEFAULT 'Upcoming',
--     created_at TEXT DEFAULT CURRENT_TIMESTAMP,
--     updated_at TEXT DEFAULT CURRENT_TIMESTAMP
--     UNIQUE(term, year)
-- );

-- -- Create 'scores' table
-- CREATE TABLE IF NOT EXISTS scores (
--     score_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     student_id INTEGER NOT NULL,
--     term_id INTEGER NOT NULL,
--     class_id INTEGER NOT NULL,
--     subject_id INTEGER NOT NULL,
--     test1 REAL,
--     test2 REAL,
--     total_test REAL,
--     exam_score REAL,
--     total_score REAL,
--     last_term_cum_bf REAL,
--     cumulative_score REAL,
--     pupils_avg REAL,
--     class_avg REAL,
--     position INTEGER,
--     grade TEXT,
--     FOREIGN KEY (student_id) REFERENCES students(student_id),
--     FOREIGN KEY (term_id) REFERENCES terms(term_id),
--     FOREIGN KEY (class_id) REFERENCES classes(class_id),
--     FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
-- );

-- -- Create 'staff_assignments' table
-- CREATE TABLE IF NOT EXISTS staff_assignments (
--     staff_id INTEGER NOT NULL,
--     class_id INTEGER NOT NULL,
--     subject_id INTEGER NOT NULL,
--     PRIMARY KEY (staff_id, class_id, subject_id),
--     FOREIGN KEY (staff_id) REFERENCES staff(staff_id),
--     FOREIGN KEY (class_id) REFERENCES classes(class_id),
--     FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
-- );

-- -- Create 'comments' table
-- CREATE TABLE IF NOT EXISTS comments (
--     comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     student_id INTEGER NOT NULL,
--     term_id INTEGER NOT NULL,
--     guardian_surname TEXT,
--     guardian_first_name TEXT,
--     guardian_middle_name TEXT,
--     class_teacher_comment TEXT,
--     guardian_comment TEXT,
--     head_teacher_comment TEXT,
--     FOREIGN KEY (student_id) REFERENCES students(student_id),
--     FOREIGN KEY (term_id) REFERENCES terms(term_id)
-- );

-- -- Create 'class_students' table
-- CREATE TABLE IF NOT EXISTS class_students (
--     class_student_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     class_id INTEGER NOT NULL,
--     student_id INTEGER NOT NULL UNIQUE,
--     FOREIGN KEY (class_id) REFERENCES classes(class_id),
--     FOREIGN KEY (student_id) REFERENCES students(student_id)
-- );

-- -- Adding Indexes
-- CREATE INDEX idx_student_id ON scores(student_id);
-- CREATE INDEX idx_class_id ON scores(class_id);

-- -- Adding Unique Constraint for Scores Table
-- CREATE UNIQUE INDEX unique_scores_idx ON scores(student_id, class_id, subject_id, term_id);

-- -- Insert Sample Data for Classes
-- INSERT INTO classes (class_name) VALUES
-- ('Pry1'), ('Pry2'), ('Pry3'), ('Pry4'), ('Pry5'), ('Pry6');

-- -- Insert Sample Data for Roles
-- INSERT INTO roles (role_name) VALUES ('student'), ('staff');

-- -- Insert Sample Data for Staff
-- INSERT INTO staff (surname, first_name, middle_name, username, password, is_admin, role_id)
-- VALUES ('Adu', 'Ayomide', 'Oluwanifesimi', 'admin', 'scrypt:32768:8:1$bltNQkwTDjLvO8Tk$503b25a489d1626404cebe8f4dad0e5d3b5f4ca8d46fc769b7007a1efb8fc90571ebe65043913ecb79a9f4829ad9fb1172dd25337f036f69cf05eb9c64b83edf', 1, (SELECT role_id FROM roles WHERE role_name = 'staff'));

-- -- Insert Sample Data for Subjects
-- INSERT INTO subjects (subject_name) VALUES
-- ('BST'), ('CREATIVE ART'), ('ENGLISH'), ('FRENCH'), ('MATHEMATICS'), ('NVE'), ('PVS'), ('RELIGION'), ('YORUBA');

-- INSERT INTO terms (term, year, is_current)
-- VALUES ('Term 2', 2025, 1);
