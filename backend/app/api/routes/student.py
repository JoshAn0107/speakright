from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
import os
import shutil
from pathlib import Path

from app.db.session import get_db
from app.api.deps import get_current_student
from app.models.user import User
from app.models.recording import Recording, RecordingStatus
from app.models.word import WordAssignment
from app.models.progress import StudentProgress
from app.schemas.recording import RecordingResponse, ProgressResponse
from app.services.pronunciation_service import pronunciation_service
from app.services.feedback_service import feedback_service
from app.core.config import settings

router = APIRouter()

# Ensure upload directory exists
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/recordings/submit", response_model=dict)
async def submit_recording(
    word_text: str = Form(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """Student submits a pronunciation recording"""

    # Validate file type
    if not audio_file.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an audio file"
        )

    # Create student-specific directory
    student_dir = UPLOAD_DIR / str(current_user.id)
    student_dir.mkdir(exist_ok=True)

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(audio_file.filename)[1]
    filename = f"{word_text.lower()}_{timestamp}{file_extension}"
    file_path = student_dir / filename

    # Save audio file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save audio file: {str(e)}"
        )

    # Assess pronunciation using Azure Speech Service
    try:
        assessment_result = pronunciation_service.assess_pronunciation(
            str(file_path),
            word_text
        )
        print(f"Assessment result: {assessment_result}")
    except Exception as e:
        import traceback
        print(f"Error calling pronunciation service: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pronunciation assessment failed: {str(e)}"
        )

    # Generate automated feedback
    try:
        automated_feedback = feedback_service.generate_feedback(assessment_result, word_text)
        print(f"Generated feedback: {automated_feedback}")
    except Exception as e:
        import traceback
        print(f"Error generating feedback: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate feedback: {str(e)}"
        )

    # Create recording entry with automated feedback
    try:
        recording = Recording(
            student_id=current_user.id,
            word_text=word_text.lower(),
            audio_file_path=str(file_path),
            automated_scores=assessment_result,
            teacher_feedback=automated_feedback['feedback_text'],
            teacher_grade=automated_feedback['grade'],
            status=RecordingStatus.REVIEWED,  # Automatically reviewed by system
            reviewed_at=datetime.utcnow()
        )

        db.add(recording)

        # Update word practice count
        word_assignment = db.query(WordAssignment).filter(
            WordAssignment.word_text == word_text.lower()
        ).first()

        if word_assignment:
            word_assignment.times_practiced += 1
        else:
            # Add word to system if not exists
            word_assignment = WordAssignment(
                word_text=word_text.lower(),
                times_practiced=1
            )
            db.add(word_assignment)

        # Update student progress for today
        today = date.today()
        progress = db.query(StudentProgress).filter(
            StudentProgress.student_id == current_user.id,
            StudentProgress.date == today
        ).first()

        if not progress:
            progress = StudentProgress(
                student_id=current_user.id,
                date=today,
                words_practiced=1,
                total_attempts=1,
                average_score=Decimal(str(assessment_result.get('pronunciation_score', 0))) if assessment_result else Decimal('0')
            )
            db.add(progress)
        else:
            progress.words_practiced += 1
            progress.total_attempts += 1

            # Update average score
            if assessment_result and 'pronunciation_score' in assessment_result:
                current_total = progress.average_score * (progress.total_attempts - 1)
                new_score = Decimal(str(assessment_result['pronunciation_score']))
                progress.average_score = (current_total + new_score) / progress.total_attempts

        db.commit()
        db.refresh(recording)
    except Exception as e:
        import traceback
        print(f"Error saving to database: {e}")
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return {
        "message": "Recording submitted and automatically reviewed",
        "recording_id": recording.id,
        "automated_scores": assessment_result,
        "feedback": {
            "text": automated_feedback['feedback_text'],
            "grade": automated_feedback['grade'],
            "is_automated": True
        }
    }


@router.get("/recordings", response_model=List[RecordingResponse])
def get_my_recordings(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """Get student's own recordings"""

    query = db.query(Recording).filter(Recording.student_id == current_user.id)

    if status:
        if status not in ["pending", "reviewed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status must be 'pending' or 'reviewed'"
            )
        query = query.filter(Recording.status == status)

    recordings = query.order_by(Recording.created_at.desc()).all()
    return recordings


@router.get("/progress", response_model=ProgressResponse)
def get_my_progress(
    period: str = "week",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """Get student's progress statistics"""

    from datetime import timedelta

    today = date.today()

    if period == "week":
        start_date = today - timedelta(days=7)
    elif period == "month":
        start_date = today - timedelta(days=30)
    else:
        start_date = None

    # Get progress records
    query = db.query(StudentProgress).filter(
        StudentProgress.student_id == current_user.id
    )

    if start_date:
        query = query.filter(StudentProgress.date >= start_date)

    progress_records = query.all()

    # Calculate statistics
    total_words = sum(p.words_practiced for p in progress_records)
    total_attempts = sum(p.total_attempts for p in progress_records)
    avg_score = sum(float(p.average_score or 0) for p in progress_records) / len(progress_records) if progress_records else 0

    # Get recent recordings
    recent_recordings = db.query(Recording).filter(
        Recording.student_id == current_user.id
    ).order_by(Recording.created_at.desc()).limit(10).all()

    recent_recordings_data = [
        {
            "id": r.id,
            "word_text": r.word_text,
            "score": r.automated_scores.get('pronunciation_score') if r.automated_scores else 0,
            "created_at": r.created_at.isoformat(),
            "status": r.status
        }
        for r in recent_recordings
    ]

    # Calculate streak
    streak = 0
    current_date = today
    while True:
        has_practice = db.query(StudentProgress).filter(
            StudentProgress.student_id == current_user.id,
            StudentProgress.date == current_date,
            StudentProgress.words_practiced > 0
        ).first()

        if has_practice:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break

    return ProgressResponse(
        words_practiced=total_words,
        average_score=round(avg_score, 2),
        total_attempts=total_attempts,
        streak_count=streak,
        recent_recordings=recent_recordings_data
    )
