import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import random
import string
from flask import make_response
from random import randint
import os

def get_db_connection():
    conn = sqlite3.connect("school_system.db")
    conn.row_factory = sqlite3.Row  # Allows fetching results as dictionaries
    return conn

# Verify user credentials
def verify_user(username, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check students
        cursor.execute("SELECT student_id AS user_id, password, first_name || ' ' || middle_name || ' ' || surname AS name FROM students WHERE username = ?", (username,))
        student = cursor.fetchone()

        if student and check_password_hash(student["password"], password):
            return {"user_id": student["user_id"], "name": student["name"], "role": "student"}

        # Check staff
        cursor.execute("SELECT staff_id AS user_id, password, first_name || ' ' || middle_name || ' ' || surname AS name, is_admin FROM staff WHERE username = ?", (username,))
        staff = cursor.fetchone()

        if staff and check_password_hash(staff["password"], password):
            return {
                "user_id": staff["user_id"],
                "name": staff["name"],
                "role": "admin" if staff["is_admin"] else "staff",
            }

    except Exception as e:
        print(f"Error verifying user: {e}")
    finally:
        conn.close()

    return None


# Register user
def register_user(form_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        role = form_data["role"]
        registration_code = form_data["registration_code"]
        hashed_password = generate_password_hash(form_data["password"])

        if role == "student":
            # Validate the registration code and get the associated class ID
            cursor.execute(
                "SELECT class_id FROM class_codes WHERE code = ? AND is_used = 0",
                (registration_code,),
            )
            class_info = cursor.fetchone()

            if class_info:
                class_id = class_info["class_id"]

                # Retrieve the role_id for the 'student' role
                cursor.execute("SELECT role_id FROM roles WHERE role_name = ?", (role,))
                role_id_result = cursor.fetchone()

                if role_id_result:
                    role_id = role_id_result["role_id"]

                    # Register the student and mark the code as used
                    cursor.execute(
                        """
                        INSERT INTO students (surname, first_name, middle_name, 
                        username, password, phone_number, email,
                        date_of_birth, address, class_id, role_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            form_data["surname"],
                            form_data["firstname"],
                            form_data["middlename"],
                            form_data["username"],
                            hashed_password,
                            form_data["phonenumber"],
                            form_data["email"],
                            form_data["date"],
                            form_data["address"],
                            class_id,
                            role_id,
                        ),
                    )
                    student_id = cursor.lastrowid

                    cursor.execute(
                        "UPDATE class_codes SET is_used = 1 WHERE code = ?",
                        (registration_code,),
                    )

                    cursor.execute(
                        "INSERT INTO class_students (class_id, student_id) VALUES (?, ?)",
                        (class_id, student_id),
                    )
                    conn.commit()
                    return True, "Student registered successfully."
                else:
                    return False, "Role ID for student not found."
            else:
                return False, "Invalid or already used registration code."

        elif role == "staff":
            cursor.execute(
                "SELECT staff_id FROM staff WHERE verification_code = ? AND code_used = 0",
                (registration_code,),
            )
            verification_result = cursor.fetchone()

            if verification_result:
                staff_id = verification_result["staff_id"]

                # Retrieve the role_id for the 'staff' role
                cursor.execute("SELECT role_id FROM roles WHERE role_name = ?", (role,))
                role_id_result = cursor.fetchone()

                if role_id_result:
                    role_id = role_id_result["role_id"]

                    # Update staff details and mark the code as used
                    cursor.execute(
                        """
                        UPDATE staff SET 
                        surname = ?, first_name = ?, middle_name = ?,
                        username = ?, password = ?, phone_number = ?, email = ?,
                        date_of_birth = ?, address = ?, role_id = ?, code_used = 1
                        WHERE staff_id = ?
                        """,
                        (
                            form_data["surname"],
                            form_data["firstname"],
                            form_data["middlename"],
                            form_data["username"],
                            hashed_password,
                            form_data["phonenumber"],
                            form_data["email"],
                            form_data["date"],
                            form_data["address"],
                            role_id,
                            staff_id,
                        ),
                    )
                    conn.commit()
                    return True, "Staff registered successfully."
                else:
                    return False, "Role not found for staff."
            else:
                return False, "Invalid or already used registration code."
        else:
            return False, "Invalid role specified."

    except Exception as e:
        print(f"Error registering user: {e}")
        return False, "Registration failed due to an error."
    finally:
        conn.close()


def get_staff_classes(staff_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT DISTINCT c.class_id, c.class_name
            FROM staff_assignments sa
            JOIN classes c ON sa.class_id = c.class_id
            WHERE sa.staff_id = ?
        """, (staff_id,))
        classes = cursor.fetchall()

        seen = set()  # Track unique class IDs
        unique_classes = []
        for class_item in classes:
            class_dict = dict(class_item)
            if class_dict['class_id'] not in seen:
                seen.add(class_dict['class_id'])
                unique_classes.append(class_dict)

        return unique_classes
    except Exception as e:
        print(f"Error fetching classes: {e}")
        return None
    finally:
        conn.close()


def get_all_classes():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''SELECT class_id AS class_id, 
                          class_name AS class_name 
                          FROM classes''')
        classes = cursor.fetchall()
        
        seen = set()  # Track unique class IDs
        unique_classes = []
        for class_item in classes:
            class_dict = dict(class_item)
            if class_dict['class_id'] not in seen:
                seen.add(class_dict['class_id'])
                unique_classes.append(class_dict)

        return unique_classes
    
    except Exception as e:
        print(f"Error fetching all classes: {e}")
        return None
    finally:
        conn.close()

def get_staff_subjects(staff_id, class_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT s.subject_id, s.subject_name
            FROM staff_assignments sa
            JOIN subjects s ON sa.subject_id = s.subject_id
            WHERE sa.staff_id = ? AND sa.class_id = ?
        """, (staff_id, class_id))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching subjects: {e}")
        return None
    finally:
        conn.close()

def get_students_by_class_and_subject(class_id, subject_id, staff_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM staff_assignments
            WHERE staff_id = ? AND class_id = ? AND subject_id = ?
        """, (staff_id, class_id, subject_id))
        is_assigned = cursor.fetchone()[0] > 0

        if not is_assigned:
            print(f"Staff {staff_id} is not assigned to class {class_id} and subject {subject_id}")
            return None

        cursor.execute("""
            SELECT s.student_id, s.surname || ' ' || s.first_name || ' ' || s.middle_name AS full_name
            FROM class_students cs
            JOIN students s ON cs.student_id = s.student_id
            WHERE cs.class_id = ?
        """, (class_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching students: {e}")
        return None
    finally:
        conn.close()

def save_student_scores(student_id, class_id, subject_id, test1, test2, exam_score, term_id, total_test, total_score, last_term_cum_bf, cumulative_score, pupils_avg):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO scores (student_id, class_id, subject_id, test1, test2, exam_score, term_id, total_test, total_score, last_term_cum_bf, cumulative_score, pupils_avg)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_id, class_id, subject_id, term_id) DO UPDATE SET
            test1 = COALESCE(EXCLUDED.test1, test1),
            test2 = COALESCE(EXCLUDED.test2, test2),
            exam_score = COALESCE(EXCLUDED.exam_score, exam_score),
            total_test = EXCLUDED.total_test,
            total_score = EXCLUDED.total_score,
            last_term_cum_bf = EXCLUDED.last_term_cum_bf,
            cumulative_score = EXCLUDED.cumulative_score,
            pupils_avg = EXCLUDED.pupils_avg
        """, (student_id, class_id, subject_id, test1, test2, exam_score, term_id, total_test, total_score, last_term_cum_bf, cumulative_score, pupils_avg))
        conn.commit()
        print("scores suceefully saved i the datbase")
        return True
    except Exception as e:
        print(f"Error saving scores: {e}")
        return False
    finally:
        conn.close()

def get_student_scores(student_id, class_id, subject_id, term_id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row  # Enables dictionary-like access
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT test1, test2, exam_score
            FROM scores
            WHERE student_id = ? AND class_id = ? AND subject_id = ? AND term_id = ?
        """, (student_id, class_id, subject_id, term_id))

        scores = dict(cursor.fetchone())

        return scores if scores else None
    
    except Exception as e:
        print(f"Error fetching scores for student {student_id}: {e}")
        return None
    finally:
        conn.close()

def get_last_term_cumulative(student_id, class_id, subject_id, current_term_id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT term, year 
            FROM terms 
            WHERE term_id = ?
        """, (current_term_id,))
        current_term_info = cursor.fetchone()

        if not current_term_info:
            return 0  

        current_term = current_term_info['term']
        current_year = current_term_info['year']

        if current_term == 'Term 1':
            return 0

        cursor.execute("""
            SELECT term_id 
            FROM terms 
            WHERE term_id < ?
            ORDER BY term_id DESC
            LIMIT 1;
        """, (current_term_id,))
        previous_term_info = cursor.fetchone()

        if not previous_term_info:
            return 0  

        previous_term_id = previous_term_info['term_id']

        cursor.execute("""
            SELECT cumulative_score 
            FROM scores 
            WHERE student_id = ? AND class_id = ? AND subject_id = ? AND term_id = ?
        """, (student_id, class_id, subject_id, previous_term_id))
        result = cursor.fetchone()

        return float(result["cumulative_score"]) if result and "cumulative_score" in result else 0
    except Exception as e:
        print(f"Error fetching last term cumulative score: {e}")
        return 0
    finally:
        conn.close()


def get_students_scores(class_id, subject_id, term_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT student_id, pupils_avg
            FROM scores
            WHERE class_id = ? AND subject_id = ? AND term_id = ?
        """, (class_id, subject_id, term_id))
        students_scores = cursor.fetchall()
        students_scores = [
            {'student_id': student['student_id'], 'pupils_avg': float(student['pupils_avg'])}
            for student in students_scores
        ]
        return students_scores
    except Exception as e:
        print(f"Error fetching students' scores: {e}")
        return []
    finally:
        conn.close()

def update_student_position_and_grade(student_id, class_id, subject_id, term_id, class_avg, position, grade):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE scores
            SET class_avg = ?, position = ?, grade = ?
            WHERE student_id = ? AND class_id = ? AND subject_id = ? AND term_id = ?
        """, (class_avg, position, grade, student_id, class_id, subject_id, term_id))
        conn.commit()
    except Exception as e:
        print(f"Error updating position and grade: {e}")
    finally:
        conn.close()

def get_current_and_next_terms():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the current term
        cursor.execute("SELECT term_id, term, year FROM terms WHERE is_current = 1 LIMIT 1")
        current_term = cursor.fetchone()

        if current_term:
            term = current_term['term']
            if term == "Term 1":
                next_term = "Term 2"
            elif term == "Term 2":
                next_term = "Term 3"
            elif term == "Term 3":
                next_term = "Term 1"
            else:
                next_term = None
        else:
            term, next_term = None, None

        return {"current_term": term, "next_term": next_term, "term_id": current_term['term_id'], "year": current_term["year"]} if current_term else {}
    except Exception as e:
        print(f"Error fetching current and next terms: {e}")
        return {"current_term": None, "next_term": None}
    finally:
        conn.close()

def set_current_term(term, year):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Reset all terms to inactive
        cursor.execute("UPDATE terms SET is_current = 0")

        # Set the specified term as current
        cursor.execute("""
            INSERT INTO terms (term, year, is_current)
            VALUES (?, ?, 1)
            ON CONFLICT(term, year) DO UPDATE SET is_current = 1, year = excluded.year
        """, (term, year))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error setting current term: {e}")
        return False
    finally:
        conn.close()

def get_all_terms():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT term_id AS id, term || ' - ' || year AS term FROM terms ORDER BY year, term"
        cursor.execute(query)
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        print(f"Error fetching all terms: {e}")
        return []
    finally:
        conn.close()

def fetch_scores_by_student(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT s.*, t.term, t.year, c.class_name, sub.subject_name
            FROM scores s
            JOIN terms t ON s.term_id = t.term_id
            JOIN classes c ON s.class_id = c.class_id
            JOIN subjects sub ON s.subject_id = sub.subject_id
            WHERE s.student_id = ?
            ORDER BY t.year, t.term
        """
        cursor.execute(query, (student_id,))
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        print(f"Error fetching scores for student_id {student_id}: {e}")
        return []
    finally:
        conn.close()

def fetch_scores_by_class_and_term(class_id, term_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT s.*, t.term, t.year, c.class_name, sub.subject_name, st.surname || ' ' || st.first_name || ' ' || st.middle_name AS student_name
            FROM scores s
            JOIN terms t ON s.term_id = t.term_id
            JOIN classes c ON s.class_id = c.class_id
            JOIN subjects sub ON s.subject_id = sub.subject_id
            JOIN students st ON s.student_id = st.student_id
            WHERE s.class_id = ? AND t.term_id = ?
            ORDER BY student_name
        """
        cursor.execute(query, (class_id, term_id))
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        print(f"Error fetching scores for class_id {class_id}, term_id {term_id}: {e}")
        return []
    finally:
        conn.close()















# Check if subject is assigned to a class
def is_subject_assigned_to_class(subject_id, class_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM staff_assignments
            WHERE class_id = ? AND subject_id = ?
        """, (class_id, subject_id))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        print(f"Error checking subject assignment: {e}")
        return False
    finally:
        conn.close()

# Check if class is assigned to staff
def is_class_assigned_to_staff(staff_id, class_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM staff_assignments 
            WHERE staff_id = ? AND class_id = ?
        """, (staff_id, class_id))
        
        result = dict(cursor.fetchone())

        return result["COUNT(*)"] > 0 
    except Exception as e:
        print(f"Error checking if class {class_id} is assigned to staff {staff_id}: {e}")
        return False
    finally:
        conn.close()

# Check if staff already exists
def is_duplicate_staff(surname, first_name, middle_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM staff 
            WHERE surname = ? AND first_name = ? AND middle_name = ?
        """, (surname, first_name, middle_name))
        result = cursor.fetchone()
        return result["count"] > 0
    except Exception as e:
        print(f"Error checking duplicate staff: {e}")
        return False
    finally:
        conn.close()

# Add Staff
def add_staff(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if staff already exists
        if is_duplicate_staff(data['surname'], data['first_name'], data['middle_name']):
            print(f"Duplicate staff detected: {data['surname']} {data['first_name']} {data['middle_name']}")
            return False  # Duplicate exists

        # Insert staff
        cursor.execute("""
            INSERT INTO staff (surname, first_name, middle_name, is_admin)
            VALUES (?, ?, ?, ?)
        """, (data['surname'], data['first_name'], data['middle_name'], int(data['is_admin'])))
        
        staff_id = cursor.lastrowid  # Get the last inserted staff_id

        # Insert staff assignments
        for assignment in data['assignments']:
            cursor.execute("""
                INSERT INTO staff_assignments (staff_id, class_id, subject_id)
                VALUES (?, ?, ?)
            """, (staff_id, assignment['class_id'], assignment['subject_id']))
        
        conn.commit()
        return True 
    
    except Exception as e:
        print(f"Error adding staff: {e}") 
        return False
    finally:
        conn.close()




# Get Staff, Class, and Subject Lists 
def get_staff_list():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM staff")
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error fetching staff list: {e}")
        return []
    finally:
        conn.close()

def get_class_list():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM classes")
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error fetching class list: {e}")
        return []
    finally:
        conn.close()

def get_subject_list():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subjects")
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error fetching subject list: {e}")
        return []
    finally:
        conn.close()

# Update Staff Assignments
def update_staff_assignments(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Remove old assignments
        cursor.execute("DELETE FROM staff_assignments WHERE staff_id = ?", (data['staff_id'],))

        # Add new assignments
        for class_id in data['class_ids']:
            for subject_id in data['subject_ids']:
                cursor.execute("""
                    INSERT INTO staff_assignments (staff_id, class_id, subject_id)
                    VALUES (?, ?, ?)
                """, (data['staff_id'], class_id, subject_id))
        conn.commit()
    except Exception as e:
        print(f"Error updating assignments: {e}")
    finally:
        conn.close()

# Get Available Classes and Subjects
def get_unassigned_classes_and_subjects():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch classes with available subjects
        cursor.execute("""
            SELECT c.class_id, c.class_name, s.subject_id, s.subject_name
            FROM classes c
            JOIN subjects s 
            WHERE s.subject_id NOT IN (
                SELECT subject_id FROM staff_assignments WHERE class_id = c.class_id
            )
        """)
        results = cursor.fetchall()

        # Organize classes and their subjects
        classes = {}
        for row in results:
            class_id = row["class_id"]
            if class_id not in classes:
                classes[class_id] = {
                    "class_name": row["class_name"],
                    "subjects": []
                }
            classes[class_id]["subjects"].append({
                "subject_id": row["subject_id"],
                "subject_name": row["subject_name"]
            })
        return classes
    except Exception as e:
        print(f"Error fetching unassigned classes and subjects: {e}")
        return {}
    finally:
        conn.close()




def get_staff_by_id(staff_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to fetch the staff details
        cursor.execute("""
            SELECT staff_id, surname, first_name, middle_name, is_admin
            FROM staff
            WHERE staff_id = ?
        """, (staff_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Error fetching staff by ID: {e}")
        return None
    finally:
        conn.close()

def get_assigned_classes_and_subjects(staff_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch assigned classes and subjects
        cursor.execute("""
            SELECT c.class_id, c.class_name, s.subject_id, s.subject_name
            FROM staff_assignments sa
            JOIN classes c ON sa.class_id = c.class_id
            JOIN subjects s ON sa.subject_id = s.subject_id
            WHERE sa.staff_id = ?
        """, (staff_id,))
        rows = cursor.fetchall()

        # Organize classes and their subjects
        classes = {}
        for row in rows:
            row = dict(row)  # Convert row to dictionary
            class_id = row["class_id"]
            if class_id not in classes:
                classes[class_id] = {'class_id': class_id, 'class_name': row["class_name"], 'subjects': []}
            classes[class_id]['subjects'].append({'subject_id': row["subject_id"], 'subject_name': row["subject_name"]})
        
        return list(classes.values())
    
    except Exception as e:
        print(f"Error getting assigned classes and subjects: {e}")
        return None
    finally:
        conn.close()

def delete_staff_classes(staff_id, class_ids):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate placeholders dynamically for IN clause
        placeholders = ', '.join(['?'] * len(class_ids))
        
        cursor.execute(f'''
            DELETE FROM staff_assignments 
            WHERE staff_id = ? AND class_id IN ({placeholders})
        ''', (staff_id, *class_ids))
        conn.commit()
    except Exception as e:
        print(f"Error deleting staff classes: {e}")
    finally:
        conn.close()

def delete_staff_subjects(staff_id, class_id, subject_ids):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        placeholders = ", ".join(["?"] * len(subject_ids))

        cursor.execute(f"""
            DELETE FROM staff_assignments
            WHERE staff_id = ? AND class_id = ? AND subject_id IN ({placeholders})
        """, (staff_id, class_id, *subject_ids))
        conn.commit()
    except Exception as e:
        print(f"Error deleting staff subjects: {e}")
    finally:
        conn.close()

def remove_staff(staff_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Remove assignments first
        cursor.execute("DELETE FROM staff_assignments WHERE staff_id = ?", (staff_id,))

        # Remove staff
        cursor.execute("DELETE FROM staff WHERE staff_id = ?", (staff_id,))
        conn.commit()
    except Exception as e:
        print(f"Error removing staff: {e}")
    finally:
        conn.close()

def assign_subject_to_staff(staff_id, class_id, subject_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert into staff_assignments
        cursor.execute("""
            INSERT INTO staff_assignments (staff_id, class_id, subject_id)
            VALUES (?, ?, ?)
        """, (staff_id, class_id, subject_id))
        conn.commit()
    except Exception as e:
        print(f"Error assigning subject to staff: {e}")
    finally:
        conn.close()

def assign_subjects_to_classes(assignments):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for assignment in assignments:
            cursor.execute("""
                INSERT INTO staff_assignments (staff_id, class_id, subject_id)
                VALUES (?, ?, ?)
            """, (assignment['staff_id'], assignment['class_id'], assignment['subject_id']))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error assigning subjects to classes: {e}")
        return False
    finally:
        conn.close()


def update_admin_status(staff_id, is_admin):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the `is_admin` field
        cursor.execute("""
            UPDATE staff
            SET is_admin = ?
            WHERE staff_id = ?
        """, (is_admin, staff_id))

        conn.commit()
    except Exception as e:
        print(f"Error updating admin status for staff {staff_id}: {e}")
        raise e
    finally:
        conn.close()

# Generate Class Codes
def generate_class_codes(batch_size=20):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all classes
        cursor.execute("SELECT class_id FROM classes")
        classes = cursor.fetchall()

        # Generate multiple codes for each class
        codes = []
        for class_row in classes:
            class_id = class_row["class_id"]
            for _ in range(batch_size):
                code = f"{class_id}{randint(1000, 9999)}"  # Unique code with class_id prefix
                codes.append((class_id, code, False))  # SQLite uses 0/1 for booleans

        # Insert the codes into the `class_codes` table
        cursor.executemany("""
            INSERT INTO class_codes (class_id, code, is_used)
            VALUES (?, ?, ?)
        """, codes)

        conn.commit()
    except Exception as e:
        print(f"Error generating class codes: {e}")
    finally:
        conn.close()

def fetch_class_codes_for_csv():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.class_name, cc.code
            FROM class_codes cc
            JOIN classes c ON cc.class_id = c.class_id
        """)
        codes = cursor.fetchall()

        # Format data for CSV
        output = [["Class", "Code"]]
        for code in codes:
            output.append([code["class_name"], code["code"]])

        return output
    except Exception as e:
        print(f"Error fetching codes for CSV: {e}")
        return []
    finally:
        conn.close()

def generate_staff_verification_codes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all staff who don't have a verification code yet
        cursor.execute("""
            SELECT staff_id FROM staff
            WHERE verification_code IS NULL
        """)

        updates = []
        for staff_row in cursor.fetchall():
            staff_id = staff_row["staff_id"]
            code = f"STF{staff_id}{datetime.now().strftime('%H%M%S')}"  # Unique staff code
            updates.append((code, staff_id))

        # Bulk update staff verification codes
        cursor.executemany("""
            UPDATE staff SET verification_code = ? WHERE staff_id = ?
        """, updates)

        conn.commit()
    except Exception as e:
        print(f"Error generating staff verification codes: {e}")
    finally:
        conn.close()

def fetch_staff_codes_for_csv():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT surname, first_name, verification_code
            FROM staff
            WHERE verification_code IS NOT NULL
        """)
        codes = cursor.fetchall()

        # Prepare CSV structure
        output = [["Surname", "First Name", "Verification Code"]]
        for row in codes:
            row_dict = dict(row)
            output.append([row_dict["surname"], row_dict["first_name"], row_dict["verification_code"]])

        return output
    except Exception as e:
        print(f"Error fetching staff codes for CSV: {e}")
        return []
    finally:
        conn.close()

def fetch_class_codes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.class_name, cc.code, cc.is_used
            FROM class_codes cc
            JOIN classes c ON cc.class_id = c.class_id
        """)
        class_codes = cursor.fetchall()

        return [dict(row) for row in class_codes]  # Convert to list of dicts
    except Exception as e:
        print(f"Error fetching class codes: {e}")
        return []
    finally:
        conn.close()

def fetch_staff_codes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT surname, first_name, verification_code, code_used
            FROM staff
            WHERE verification_code IS NOT NULL
        """)
        staff_codes = cursor.fetchall()

        return [dict(row) for row in staff_codes]  # Convert to list of dicts
    except Exception as e:
        print(f"Error fetching staff codes: {e}")
        return []
    finally:
        conn.close()