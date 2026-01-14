#!/usr/bin/env python3
"""
Test script for the assignment system
Tests all assignment endpoints as both teacher and student
"""

import requests
import json
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_result(test_name, success, details=""):
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"    {details}")

def get_test_users():
    """Get a teacher and student from database"""
    db = SessionLocal()
    try:
        # Use actual teacher: ajiang@ed.ac.uk password: An20120912
        teacher = db.query(User).filter(User.email == "ajiang@ed.ac.uk").first()
        # Get any student for testing
        student = db.query(User).filter(User.role == "student").first()
        return teacher, student
    finally:
        db.close()

def login(email, password):
    """Login and get access token"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed for {email}: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Login error for {email}: {str(e)}")
        return None

def test_word_databases(token):
    """Test getting word databases"""
    print_section("Testing Word Databases")

    try:
        response = requests.get(
            f"{BASE_URL}/api/assignments/databases",
            headers={"Authorization": f"Bearer {token}"}
        )

        success = response.status_code == 200
        if success:
            databases = response.json()
            print_result("Get word databases", True, f"Found {len(databases)} databases")
            for db in databases:
                print(f"    - {db['name']}: {db['word_count']} words")
            return databases
        else:
            print_result("Get word databases", False, f"Status {response.status_code}: {response.text}")
            return []
    except Exception as e:
        print_result("Get word databases", False, str(e))
        return []

def test_database_words(token, database_id):
    """Test getting words from a database"""
    print_section(f"Testing Database Words (ID: {database_id})")

    try:
        response = requests.get(
            f"{BASE_URL}/api/assignments/databases/{database_id}/words",
            headers={"Authorization": f"Bearer {token}"}
        )

        success = response.status_code == 200
        if success:
            words = response.json()
            print_result("Get database words", True, f"Found {len(words)} words")
            print(f"    First 5 words: {', '.join([w['word_text'] for w in words[:5]])}")
            return words
        else:
            print_result("Get database words", False, f"Status {response.status_code}")
            return []
    except Exception as e:
        print_result("Get database words", False, str(e))
        return []

def test_create_assignment(teacher_token, database_id, word_texts, student_ids):
    """Test creating an assignment"""
    print_section("Testing Create Assignment")

    assignment_data = {
        "title": "Test Assignment - IELTS Practice",
        "description": "Practice assignment for testing",
        "word_database_id": database_id,
        "due_date": "2025-12-31T23:59:59",
        "words": word_texts[:25],  # Take 25 words
        "student_ids": student_ids
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/assignments/teacher/assignments",
            headers={"Authorization": f"Bearer {teacher_token}"},
            json=assignment_data
        )

        success = response.status_code == 200
        if success:
            assignment = response.json()
            print_result("Create assignment", True,
                        f"Created assignment ID {assignment['id']}: '{assignment['title']}'")
            print(f"    Words: {len(word_texts[:25])}")
            print(f"    Students: {len(student_ids)}")
            return assignment
        else:
            print_result("Create assignment", False,
                        f"Status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_result("Create assignment", False, str(e))
        return None

def test_get_teacher_assignments(teacher_token):
    """Test getting teacher's assignments"""
    print_section("Testing Get Teacher Assignments")

    try:
        response = requests.get(
            f"{BASE_URL}/api/assignments/teacher/assignments",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        success = response.status_code == 200
        if success:
            assignments = response.json()
            print_result("Get teacher assignments", True, f"Found {len(assignments)} assignments")
            for assignment in assignments:
                print(f"    - {assignment['title']} ({assignment['student_count']} students, {assignment['word_count']} words)")
            return assignments
        else:
            print_result("Get teacher assignments", False, f"Status {response.status_code}")
            return []
    except Exception as e:
        print_result("Get teacher assignments", False, str(e))
        return []

def test_get_student_assignments(student_token):
    """Test getting student's assignments"""
    print_section("Testing Get Student Assignments")

    try:
        response = requests.get(
            f"{BASE_URL}/api/assignments/student/assignments",
            headers={"Authorization": f"Bearer {student_token}"}
        )

        success = response.status_code == 200
        if success:
            assignments = response.json()
            print_result("Get student assignments", True, f"Found {len(assignments)} assignments")
            for assignment in assignments:
                print(f"    - {assignment['title']} - {assignment['completion_percentage']}% complete ({assignment['completed_words']}/{assignment['total_words']})")
            return assignments
        else:
            print_result("Get student assignments", False, f"Status {response.status_code}")
            return []
    except Exception as e:
        print_result("Get student assignments", False, str(e))
        return []

def test_assignment_progress(teacher_token, assignment_id):
    """Test getting assignment progress"""
    print_section(f"Testing Assignment Progress (ID: {assignment_id})")

    try:
        response = requests.get(
            f"{BASE_URL}/api/assignments/teacher/assignments/{assignment_id}/progress",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        success = response.status_code == 200
        if success:
            progress = response.json()
            print_result("Get assignment progress", True, f"{len(progress)} students")
            for student_progress in progress:
                print(f"    - {student_progress['student_name']}: {student_progress['completion_percentage']}% ({student_progress['completed_words']}/{student_progress['total_words']} words)")
            return progress
        else:
            print_result("Get assignment progress", False, f"Status {response.status_code}")
            return []
    except Exception as e:
        print_result("Get assignment progress", False, str(e))
        return []

def main():
    print("\n" + "="*60)
    print("  ASSIGNMENT SYSTEM TEST SUITE")
    print("="*60)

    # Get test users
    print("\nGetting test users from database...")
    teacher, student = get_test_users()

    if not teacher:
        print("✗ No teacher found in database!")
        return
    if not student:
        print("✗ No student found in database!")
        return

    print(f"✓ Teacher: {teacher.username}")
    print(f"✓ Student: {student.username}")

    # Login as teacher
    print("\nLogging in as teacher...")
    teacher_token = login(teacher.email, "An20120912")
    if not teacher_token:
        print("✗ Teacher login failed!")
        return
    print("✓ Teacher logged in successfully")

    # Login as student - try common passwords
    print("\nLogging in as student...")
    student_token = None
    for password in ["password123", "An20120912", "student123", "test123"]:
        student_token = login(student.email, password)
        if student_token:
            break

    if not student_token:
        print(f"✗ Student login failed for {student.email}! Please provide correct password.")
        return
    print("✓ Student logged in successfully")

    # Test word databases
    databases = test_word_databases(teacher_token)
    if not databases:
        print("\n✗ Cannot continue - no word databases found")
        return

    # Test database words
    database_id = databases[0]['id']
    words = test_database_words(teacher_token, database_id)
    if not words:
        print("\n✗ Cannot continue - no words found in database")
        return

    # Test create assignment
    word_texts = [w['word_text'] for w in words]
    student_ids = [student.id]
    assignment = test_create_assignment(teacher_token, database_id, word_texts, student_ids)

    # Test get teacher assignments
    teacher_assignments = test_get_teacher_assignments(teacher_token)

    # Test get student assignments
    student_assignments = test_get_student_assignments(student_token)

    # Test assignment progress
    if assignment:
        test_assignment_progress(teacher_token, assignment['id'])

    # Summary
    print_section("TEST SUMMARY")
    print("All core assignment endpoints have been tested.")
    print("Check the results above for any failures.")
    print("\nTo test the full workflow:")
    print("1. Student records pronunciations")
    print("2. Submit recordings to assignment")
    print("3. Check progress updates")

if __name__ == "__main__":
    main()
