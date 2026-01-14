from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.api.deps import get_current_teacher, get_current_student, get_current_user
from app.models.user import User
from app.models.assignment import (
    WordDatabase, WordDatabaseWord, Assignment, AssignmentWord,
    AssignmentStudent, AssignmentSubmission
)
from app.models.recording import Recording
from app.schemas.assignment import (
    WordDatabaseResponse, WordDatabaseWordResponse,
    AssignmentCreate, AssignmentUpdate, AssignmentResponse,
    StudentAssignmentResponse, AssignmentProgressResponse,
    AssignmentSubmissionCreate
)

router = APIRouter()


# ===== Word Database Endpoints =====

@router.get("/databases", response_model=List[WordDatabaseResponse])
def get_word_databases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available word databases"""
    databases = db.query(WordDatabase).all()
    return databases


@router.get("/databases/{database_id}/words", response_model=List[WordDatabaseWordResponse])
def get_database_words(
    database_id: int,
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get words from a specific database"""
    database = db.query(WordDatabase).filter(WordDatabase.id == database_id).first()
    if not database:
        raise HTTPException(status_code=404, detail="Word database not found")

    words = db.query(WordDatabaseWord).filter(
        WordDatabaseWord.database_id == database_id
    ).offset(skip).limit(limit).all()

    return words


# ===== Teacher Assignment Endpoints =====

@router.post("/teacher/assignments", response_model=AssignmentResponse)
def create_assignment(
    assignment_data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Teacher creates a new assignment"""

    # Validate word count (20-40 words)
    word_count = len(assignment_data.words)
    if word_count < 20 or word_count > 40:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Assignment must contain 20-40 words. Got {word_count} words."
        )

    # Validate student IDs
    if not assignment_data.student_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one student must be assigned"
        )

    students = db.query(User).filter(
        User.id.in_(assignment_data.student_ids),
        User.role == "student"
    ).all()

    if len(students) != len(assignment_data.student_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more invalid student IDs"
        )

    # Create assignment
    assignment = Assignment(
        teacher_id=current_user.id,
        title=assignment_data.title,
        description=assignment_data.description,
        word_database_id=assignment_data.word_database_id,
        due_date=assignment_data.due_date
    )
    db.add(assignment)
    db.flush()  # Get assignment ID

    # Add words to assignment
    for index, word_text in enumerate(assignment_data.words):
        assignment_word = AssignmentWord(
            assignment_id=assignment.id,
            word_text=word_text.lower().strip(),
            order_index=index
        )
        db.add(assignment_word)

    # Assign to students
    for student_id in assignment_data.student_ids:
        assignment_student = AssignmentStudent(
            assignment_id=assignment.id,
            student_id=student_id
        )
        db.add(assignment_student)

    db.commit()
    db.refresh(assignment)

    # Build response
    return build_assignment_response(assignment, db)


@router.get("/teacher/assignments", response_model=List[AssignmentResponse])
def get_teacher_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Get all assignments created by the teacher"""
    assignments = db.query(Assignment).filter(
        Assignment.teacher_id == current_user.id
    ).order_by(Assignment.created_at.desc()).all()

    return [build_assignment_response(assignment, db) for assignment in assignments]


@router.get("/teacher/assignments/{assignment_id}", response_model=AssignmentResponse)
def get_teacher_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Get a specific assignment created by the teacher"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == current_user.id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    return build_assignment_response(assignment, db)


@router.put("/teacher/assignments/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(
    assignment_id: int,
    assignment_data: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Update an assignment"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == current_user.id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Update fields
    if assignment_data.title is not None:
        assignment.title = assignment_data.title
    if assignment_data.description is not None:
        assignment.description = assignment_data.description
    if assignment_data.due_date is not None:
        assignment.due_date = assignment_data.due_date

    db.commit()
    db.refresh(assignment)

    return build_assignment_response(assignment, db)


@router.delete("/teacher/assignments/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Delete an assignment"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == current_user.id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    db.delete(assignment)
    db.commit()

    return {"message": "Assignment deleted successfully"}


@router.get("/teacher/assignments/{assignment_id}/progress", response_model=List[dict])
def get_assignment_progress(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Get detailed progress for all students on an assignment"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == current_user.id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    total_words = len(assignment.words)
    student_progress = []

    for assignment_student in assignment.students:
        student = assignment_student.student

        # Count completed words
        completed_count = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.student_id == student.id
        ).count()

        completion_percentage = (completed_count / total_words * 100) if total_words > 0 else 0

        student_progress.append({
            "student_id": student.id,
            "student_name": student.username,
            "total_words": total_words,
            "completed_words": completed_count,
            "completion_percentage": round(completion_percentage, 1),
            "assigned_at": assignment_student.assigned_at,
            "completed_at": assignment_student.completed_at
        })

    return student_progress


@router.get("/teacher/assignments/{assignment_id}/students/{student_id}/progress")
def get_student_progress_for_teacher(
    assignment_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Get detailed word-by-word progress for a specific student on an assignment (teacher view)"""
    # Verify teacher owns this assignment
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == current_user.id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Verify student is assigned to this assignment
    assignment_student = db.query(AssignmentStudent).filter(
        AssignmentStudent.assignment_id == assignment_id,
        AssignmentStudent.student_id == student_id
    ).first()

    if not assignment_student:
        raise HTTPException(status_code=404, detail="Student not assigned to this assignment")

    # Get all words in assignment
    assignment_words = db.query(AssignmentWord).filter(
        AssignmentWord.assignment_id == assignment_id
    ).order_by(AssignmentWord.order_index).all()

    # Get submissions for this student
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == student_id
    ).all()

    submission_dict = {sub.word_text: sub for sub in submissions}

    word_list = []
    for word in assignment_words:
        submission = submission_dict.get(word.word_text)
        word_info = {
            "word_text": word.word_text,
            "order_index": word.order_index,
            "submitted": submission is not None,
            "recording_id": submission.recording_id if submission else None,
            "submitted_at": submission.submitted_at if submission else None
        }

        # Get score if recording exists
        if submission and submission.recording_id:
            recording = db.query(Recording).filter(Recording.id == submission.recording_id).first()
            if recording and recording.automated_scores:
                word_info["score"] = recording.automated_scores.get("pronunciation_score", 0)

        word_list.append(word_info)

    total_words = len(assignment_words)
    completed_words = len([w for w in word_list if w["submitted"]])

    return {
        "assignment_id": assignment_id,
        "assignment_title": assignment.title,
        "student_id": student_id,
        "total_words": total_words,
        "completed_words": completed_words,
        "completion_percentage": round((completed_words / total_words * 100), 1) if total_words > 0 else 0,
        "completed_word_texts": [w["word_text"] for w in word_list if w["submitted"]],
        "words": word_list
    }


# ===== Student Assignment Endpoints =====

@router.get("/student/assignments", response_model=List[StudentAssignmentResponse])
def get_student_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """Get all assignments for the current student"""
    assignment_students = db.query(AssignmentStudent).filter(
        AssignmentStudent.student_id == current_user.id
    ).all()

    assignments = []
    for assignment_student in assignment_students:
        assignment = assignment_student.assignment
        assignments.append(build_student_assignment_response(assignment, current_user.id, db))

    return assignments


@router.get("/student/assignments/{assignment_id}", response_model=StudentAssignmentResponse)
def get_student_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """Get a specific assignment for the student"""
    assignment_student = db.query(AssignmentStudent).filter(
        AssignmentStudent.assignment_id == assignment_id,
        AssignmentStudent.student_id == current_user.id
    ).first()

    if not assignment_student:
        raise HTTPException(status_code=404, detail="Assignment not found")

    assignment = assignment_student.assignment
    return build_student_assignment_response(assignment, current_user.id, db)


@router.post("/student/assignments/{assignment_id}/submit")
def submit_assignment_word(
    assignment_id: int,
    word_text: str,
    recording_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """Submit a word recording for an assignment"""
    # Verify student has this assignment
    assignment_student = db.query(AssignmentStudent).filter(
        AssignmentStudent.assignment_id == assignment_id,
        AssignmentStudent.student_id == current_user.id
    ).first()

    if not assignment_student:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Verify word is in assignment
    assignment_word = db.query(AssignmentWord).filter(
        AssignmentWord.assignment_id == assignment_id,
        AssignmentWord.word_text == word_text.lower().strip()
    ).first()

    if not assignment_word:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Word not in assignment"
        )

    # Verify recording belongs to student
    recording = db.query(Recording).filter(
        Recording.id == recording_id,
        Recording.student_id == current_user.id
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Check if submission already exists (allow re-recording)
    existing_submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == current_user.id,
        AssignmentSubmission.word_text == word_text.lower().strip()
    ).first()

    if existing_submission:
        # Update existing submission
        existing_submission.recording_id = recording_id
        existing_submission.submitted_at = datetime.utcnow()
    else:
        # Create new submission
        submission = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=current_user.id,
            word_text=word_text.lower().strip(),
            recording_id=recording_id
        )
        db.add(submission)

    # Check if assignment is complete
    total_words = db.query(AssignmentWord).filter(
        AssignmentWord.assignment_id == assignment_id
    ).count()

    completed_words = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == current_user.id
    ).count()

    if completed_words >= total_words and not assignment_student.completed_at:
        assignment_student.completed_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Word submitted successfully",
        "completed_words": completed_words,
        "total_words": total_words,
        "completion_percentage": round((completed_words / total_words * 100), 1) if total_words > 0 else 0
    }


@router.get("/student/assignments/{assignment_id}/progress")
def get_student_assignment_progress(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """Get student's progress on a specific assignment"""
    assignment_student = db.query(AssignmentStudent).filter(
        AssignmentStudent.assignment_id == assignment_id,
        AssignmentStudent.student_id == current_user.id
    ).first()

    if not assignment_student:
        raise HTTPException(status_code=404, detail="Assignment not found")

    assignment = assignment_student.assignment

    # Get all words in assignment
    assignment_words = db.query(AssignmentWord).filter(
        AssignmentWord.assignment_id == assignment_id
    ).order_by(AssignmentWord.order_index).all()

    # Get submissions
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == current_user.id
    ).all()

    submission_dict = {sub.word_text: sub for sub in submissions}

    word_list = []
    for word in assignment_words:
        submission = submission_dict.get(word.word_text)
        word_info = {
            "word_text": word.word_text,
            "order_index": word.order_index,
            "submitted": submission is not None,
            "recording_id": submission.recording_id if submission else None,
            "submitted_at": submission.submitted_at if submission else None
        }

        # Get score if recording exists
        if submission and submission.recording_id:
            recording = db.query(Recording).filter(Recording.id == submission.recording_id).first()
            if recording and recording.automated_scores:
                word_info["score"] = recording.automated_scores.get("pronunciation_score", 0)

        word_list.append(word_info)

    total_words = len(assignment_words)
    completed_words = len([w for w in word_list if w["submitted"]])

    return {
        "assignment_id": assignment_id,
        "assignment_title": assignment.title,
        "total_words": total_words,
        "completed_words": completed_words,
        "completion_percentage": round((completed_words / total_words * 100), 1) if total_words > 0 else 0,
        "words": word_list
    }


# ===== Helper Functions =====

def build_assignment_response(assignment: Assignment, db: Session) -> dict:
    """Build assignment response with additional data"""
    word_count = len(assignment.words)
    student_count = len(assignment.students)

    # Get word database name if exists
    word_database_name = None
    if assignment.word_database_id:
        database = db.query(WordDatabase).filter(WordDatabase.id == assignment.word_database_id).first()
        if database:
            word_database_name = database.name

    return {
        "id": assignment.id,
        "teacher_id": assignment.teacher_id,
        "title": assignment.title,
        "description": assignment.description,
        "word_database_id": assignment.word_database_id,
        "word_database_name": word_database_name,
        "due_date": assignment.due_date,
        "created_at": assignment.created_at,
        "updated_at": assignment.updated_at,
        "words": [
            {
                "id": w.id,
                "word_text": w.word_text,
                "order_index": w.order_index
            }
            for w in sorted(assignment.words, key=lambda x: x.order_index)
        ],
        "word_count": word_count,
        "student_count": student_count
    }


def build_student_assignment_response(assignment: Assignment, student_id: int, db: Session) -> dict:
    """Build assignment response from student's perspective"""
    # Get teacher info
    teacher = db.query(User).filter(User.id == assignment.teacher_id).first()
    teacher_name = teacher.username if teacher else "Unknown"

    # Get word database name
    word_database_name = None
    if assignment.word_database_id:
        database = db.query(WordDatabase).filter(WordDatabase.id == assignment.word_database_id).first()
        if database:
            word_database_name = database.name

    # Get assignment student record
    assignment_student = db.query(AssignmentStudent).filter(
        AssignmentStudent.assignment_id == assignment.id,
        AssignmentStudent.student_id == student_id
    ).first()

    # Calculate progress
    total_words = len(assignment.words)
    completed_words = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment.id,
        AssignmentSubmission.student_id == student_id
    ).count()

    completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0

    # Check if overdue
    is_overdue = False
    if assignment.due_date and datetime.utcnow() > assignment.due_date.replace(tzinfo=None):
        is_overdue = True

    return {
        "id": assignment.id,
        "title": assignment.title,
        "description": assignment.description,
        "teacher_name": teacher_name,
        "word_database_name": word_database_name,
        "due_date": assignment.due_date,
        "assigned_at": assignment_student.assigned_at if assignment_student else None,
        "completed_at": assignment_student.completed_at if assignment_student else None,
        "words": [
            {
                "id": w.id,
                "word_text": w.word_text,
                "order_index": w.order_index
            }
            for w in sorted(assignment.words, key=lambda x: x.order_index)
        ],
        "total_words": total_words,
        "completed_words": completed_words,
        "completion_percentage": round(completion_percentage, 1),
        "is_overdue": is_overdue
    }
