from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.api.deps import get_current_teacher
from app.models.user import User, UserRole
from app.models.recording import Recording, RecordingStatus
from app.models.classes import Class, ClassEnrollment
from app.schemas.recording import RecordingResponse, TeacherFeedbackCreate

router = APIRouter()


@router.get("/submissions", response_model=List[dict])
def get_submissions(
    status_filter: Optional[str] = None,
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Get student submissions for review"""

    query = db.query(Recording).join(User, Recording.student_id == User.id)

    # Filter by status
    if status_filter:
        if status_filter not in ["pending", "reviewed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status must be 'pending' or 'reviewed'"
            )
        query = query.filter(Recording.status == status_filter)

    # Filter by class
    if class_id:
        # Verify teacher owns this class
        class_obj = db.query(Class).filter(
            Class.id == class_id,
            Class.teacher_id == current_user.id
        ).first()

        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )

        # Get students in this class
        student_ids = db.query(ClassEnrollment.student_id).filter(
            ClassEnrollment.class_id == class_id
        ).all()
        student_ids = [sid[0] for sid in student_ids]

        query = query.filter(Recording.student_id.in_(student_ids))

    recordings = query.order_by(desc(Recording.created_at)).all()

    # Format response with student info
    result = []
    for recording in recordings:
        student = db.query(User).filter(User.id == recording.student_id).first()
        result.append({
            "id": recording.id,
            "student_id": recording.student_id,
            "student_name": student.username if student else "Unknown",
            "word_text": recording.word_text,
            "audio_file_path": recording.audio_file_path,
            "automated_scores": recording.automated_scores,
            "teacher_feedback": recording.teacher_feedback,
            "teacher_grade": recording.teacher_grade,
            "status": recording.status,
            "flag_for_practice": recording.flag_for_practice,
            "is_automated_feedback": recording.is_automated_feedback if hasattr(recording, 'is_automated_feedback') else True,
            "created_at": recording.created_at,
            "reviewed_at": recording.reviewed_at
        })

    return result


@router.post("/feedback", response_model=dict)
def submit_feedback(
    feedback: TeacherFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Submit teacher feedback on a recording"""

    # Get recording
    recording = db.query(Recording).filter(Recording.id == feedback.recording_id).first()

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    # Update recording with feedback
    if feedback.feedback_text:
        recording.teacher_feedback = feedback.feedback_text
    if feedback.grade:
        recording.teacher_grade = feedback.grade

    recording.flag_for_practice = feedback.flag_for_practice
    recording.reviewed_by = current_user.id
    recording.status = RecordingStatus.REVIEWED
    recording.reviewed_at = datetime.utcnow()
    recording.is_automated_feedback = False  # Mark as manually reviewed by teacher

    db.commit()

    return {
        "message": "Teacher feedback updated successfully",
        "recording_id": recording.id,
        "previous_feedback_was_automated": recording.is_automated_feedback
    }


@router.get("/students", response_model=List[dict])
def get_students(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Get list of students"""

    if class_id:
        # Get students in specific class
        class_obj = db.query(Class).filter(
            Class.id == class_id,
            Class.teacher_id == current_user.id
        ).first()

        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )

        student_ids = db.query(ClassEnrollment.student_id).filter(
            ClassEnrollment.class_id == class_id
        ).all()
        student_ids = [sid[0] for sid in student_ids]

        students = db.query(User).filter(
            User.id.in_(student_ids),
            User.role == UserRole.STUDENT
        ).all()
    else:
        # Get all students
        students = db.query(User).filter(User.role == UserRole.STUDENT).all()

    # Get statistics for each student
    result = []
    for student in students:
        # Get all recordings for this student
        recordings = db.query(Recording).filter(
            Recording.student_id == student.id
        ).all()

        total_recordings = len(recordings)

        # Calculate average score in Python to avoid SQLAlchemy JSON field caching issues
        scores = [
            r.automated_scores.get('pronunciation_score')
            for r in recordings
            if r.automated_scores and 'pronunciation_score' in r.automated_scores
        ]
        avg_score = sum(scores) / len(scores) if scores else 0

        result.append({
            "id": student.id,
            "username": student.username,
            "email": student.email,
            "total_recordings": total_recordings,
            "average_score": round(float(avg_score), 2) if avg_score else 0
        })

    return result


@router.get("/analytics", response_model=dict)
def get_analytics(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Get analytics and statistics"""

    query = db.query(Recording)

    if class_id:
        # Filter by class
        class_obj = db.query(Class).filter(
            Class.id == class_id,
            Class.teacher_id == current_user.id
        ).first()

        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )

        student_ids = db.query(ClassEnrollment.student_id).filter(
            ClassEnrollment.class_id == class_id
        ).all()
        student_ids = [sid[0] for sid in student_ids]

        query = query.filter(Recording.student_id.in_(student_ids))

    # Total recordings
    total_recordings = query.count()

    # Pending reviews
    pending_reviews = query.filter(Recording.status == RecordingStatus.PENDING).count()

    # Average score across all recordings
    avg_score = db.query(func.avg(
        func.cast(Recording.automated_scores['pronunciation_score'], func.Float)
    )).filter(
        Recording.automated_scores.isnot(None)
    ).scalar()

    # Most practiced words
    word_counts = db.query(
        Recording.word_text,
        func.count(Recording.id).label('count')
    ).group_by(Recording.word_text).order_by(desc('count')).limit(10).all()

    most_practiced_words = [
        {"word": word, "count": count}
        for word, count in word_counts
    ]

    # Words with lowest average scores (challenging words)
    challenging_words = db.query(
        Recording.word_text,
        func.avg(func.cast(Recording.automated_scores['pronunciation_score'], func.Float)).label('avg_score')
    ).filter(
        Recording.automated_scores.isnot(None)
    ).group_by(Recording.word_text).order_by('avg_score').limit(10).all()

    challenging_words_list = [
        {"word": word, "average_score": round(float(score), 2) if score else 0}
        for word, score in challenging_words
    ]

    return {
        "total_recordings": total_recordings,
        "pending_reviews": pending_reviews,
        "average_score": round(float(avg_score), 2) if avg_score else 0,
        "most_practiced_words": most_practiced_words,
        "challenging_words": challenging_words_list
    }


@router.post("/classes", response_model=dict)
def create_class(
    class_name: str,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Create a new class"""

    new_class = Class(
        teacher_id=current_user.id,
        class_name=class_name,
        description=description
    )

    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    return {
        "message": "Class created successfully",
        "class_id": new_class.id,
        "class_name": new_class.class_name
    }


@router.get("/classes", response_model=List[dict])
def get_my_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Get teacher's classes"""

    classes = db.query(Class).filter(Class.teacher_id == current_user.id).all()

    result = []
    for class_obj in classes:
        # Count students
        student_count = db.query(func.count(ClassEnrollment.id)).filter(
            ClassEnrollment.class_id == class_obj.id
        ).scalar()

        result.append({
            "id": class_obj.id,
            "class_name": class_obj.class_name,
            "description": class_obj.description,
            "student_count": student_count or 0,
            "created_at": class_obj.created_at
        })

    return result
