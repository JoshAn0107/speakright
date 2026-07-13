from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from collections import Counter, defaultdict
from typing import List, Optional
from datetime import datetime
import secrets

from app.db.session import get_db
from app.api.deps import get_current_teacher
from app.models.user import User, UserRole
from app.models.recording import Recording, RecordingStatus
from app.models.classes import Class, ClassEnrollment
from app.models.suggestion import FeatureSuggestion
from app.schemas.recording import RecordingResponse, TeacherFeedbackCreate

router = APIRouter()


def _teacher_student_ids(db: Session, teacher_id: int) -> list:
    """Student ids enrolled in any of this teacher's classes"""
    rows = db.query(ClassEnrollment.student_id).join(
        Class, ClassEnrollment.class_id == Class.id
    ).filter(Class.teacher_id == teacher_id).distinct().all()
    return [r[0] for r in rows]


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
                detail="状态必须为 'pending' 或 'reviewed'"
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
                detail="未找到班级"
            )

        # Get students in this class
        student_ids = db.query(ClassEnrollment.student_id).filter(
            ClassEnrollment.class_id == class_id
        ).all()
        student_ids = [sid[0] for sid in student_ids]

        query = query.filter(Recording.student_id.in_(student_ids))
    else:
        # No class filter: still only show recordings from this teacher's own students
        query = query.filter(Recording.student_id.in_(_teacher_student_ids(db, current_user.id)))

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
            detail="未找到录音"
        )

    if recording.student_id not in _teacher_student_ids(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能评审自己班级学生的录音"
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
        "message": "教师反馈更新成功",
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
                detail="未找到班级"
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
        # All students across this teacher's own classes only
        students = db.query(User).filter(
            User.id.in_(_teacher_student_ids(db, current_user.id)),
            User.role == UserRole.STUDENT
        ).all()

    # One aggregate query instead of loading every recording per student
    student_ids_list = [s.id for s in students]
    stats = {}
    if student_ids_list:
        rows = db.query(
            Recording.student_id,
            func.count(Recording.id),
            func.avg(func.nullif(func.json_extract(Recording.automated_scores, "$.pronunciation_score"), 0))
        ).filter(
            Recording.student_id.in_(student_ids_list)
        ).group_by(Recording.student_id).all()
        stats = {r[0]: (r[1], r[2]) for r in rows}

    result = []
    for student in students:
        total, avg_score = stats.get(student.id, (0, None))
        result.append({
            "id": student.id,
            "username": student.username,
            "email": student.email,
            "total_recordings": total,
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
                detail="未找到班级"
            )

        student_ids = db.query(ClassEnrollment.student_id).filter(
            ClassEnrollment.class_id == class_id
        ).all()
        student_ids = [sid[0] for sid in student_ids]

        query = query.filter(Recording.student_id.in_(student_ids))
    else:
        query = query.filter(Recording.student_id.in_(_teacher_student_ids(db, current_user.id)))

    # aggregate everything in SQL — never load full recordings into Python
    score_expr = func.json_extract(Recording.automated_scores, "$.pronunciation_score")

    total_recordings = query.count()
    pending_reviews = query.filter(Recording.status == RecordingStatus.PENDING).count()
    avg_score = query.with_entities(func.avg(func.nullif(score_expr, 0))).scalar() or 0

    word_rows = query.with_entities(
        Recording.word_text,
        func.count(Recording.id),
        func.avg(func.nullif(score_expr, 0))
    ).filter(Recording.word_text.isnot(None)).group_by(Recording.word_text).all()

    most_practiced_words = [
        {"word": w, "count": c}
        for w, c, _ in sorted(word_rows, key=lambda r: -r[1])[:10]
    ]
    challenging_words_list = [
        {"word": w, "average_score": round(float(a), 2)}
        for w, _, a in sorted((r for r in word_rows if r[2] is not None), key=lambda r: r[2])[:10]
    ]

    return {
        "total_recordings": total_recordings,
        "pending_reviews": pending_reviews,
        "average_score": round(float(avg_score), 2) if avg_score else 0,
        "most_practiced_words": most_practiced_words,
        "challenging_words": challenging_words_list
    }


def _generate_class_code(db: Session) -> str:
    """Generate a unique 6-character class code (unambiguous characters only)"""
    alphabet = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # no 0/O, 1/I/L
    for _ in range(20):
        code = "".join(secrets.choice(alphabet) for _ in range(6))
        if not db.query(Class).filter(Class.class_code == code).first():
            return code
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="无法生成班级码，请重试"
    )


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
        description=description,
        class_code=_generate_class_code(db)
    )

    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    return {
        "message": "班级创建成功",
        "class_id": new_class.id,
        "class_name": new_class.class_name,
        "class_code": new_class.class_code
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

        # Backfill a code for classes created before class codes existed
        if not class_obj.class_code:
            class_obj.class_code = _generate_class_code(db)
            db.commit()

        result.append({
            "id": class_obj.id,
            "class_name": class_obj.class_name,
            "description": class_obj.description,
            "class_code": class_obj.class_code,
            "student_count": student_count or 0,
            "created_at": class_obj.created_at
        })

    return result


def _get_owned_class(class_id: int, db: Session, current_user: User) -> Class:
    class_obj = db.query(Class).filter(
        Class.id == class_id,
        Class.teacher_id == current_user.id
    ).first()
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到班级"
        )
    return class_obj


@router.put("/classes/{class_id}", response_model=dict)
def update_class(
    class_id: int,
    class_name: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Update class name and/or description"""

    class_obj = _get_owned_class(class_id, db, current_user)

    if class_name is not None and class_name.strip():
        class_obj.class_name = class_name.strip()
    if description is not None:
        class_obj.description = description.strip() or None

    db.commit()

    return {
        "message": "班级更新成功",
        "class_id": class_obj.id,
        "class_name": class_obj.class_name,
        "description": class_obj.description
    }


@router.delete("/classes/{class_id}", response_model=dict)
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Delete a class and its enrollments (students themselves are kept)"""

    class_obj = _get_owned_class(class_id, db, current_user)

    db.query(ClassEnrollment).filter(
        ClassEnrollment.class_id == class_obj.id
    ).delete()
    db.delete(class_obj)
    db.commit()

    return {"message": "班级已删除", "class_id": class_id}


@router.delete("/classes/{class_id}/students/{student_id}", response_model=dict)
def remove_student_from_class(
    class_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Remove a student from a class"""

    _get_owned_class(class_id, db, current_user)

    enrollment = db.query(ClassEnrollment).filter(
        ClassEnrollment.class_id == class_id,
        ClassEnrollment.student_id == student_id
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该学生不在此班级中"
        )

    db.delete(enrollment)
    db.commit()

    return {"message": "已将学生移出班级", "class_id": class_id, "student_id": student_id}


@router.post("/suggestions", response_model=dict)
def create_suggestion(
    content: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Teacher leaves feedback / a feature request for the platform"""

    text = content.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="留言内容不能为空"
        )
    if len(text) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="留言不能超过2000字"
        )

    suggestion = FeatureSuggestion(
        teacher_id=current_user.id,
        content=text,
        status="new"
    )
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)

    return {
        "message": "感谢反馈！我们会尽快查看你的建议。",
        "suggestion_id": suggestion.id
    }


@router.get("/suggestions", response_model=List[dict])
def get_my_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """List the teacher's own feedback messages with replies"""

    suggestions = db.query(FeatureSuggestion).filter(
        FeatureSuggestion.teacher_id == current_user.id
    ).order_by(FeatureSuggestion.created_at.desc()).all()

    return [
        {
            "id": s.id,
            "content": s.content,
            "status": s.status,
            "reply": s.reply,
            "created_at": s.created_at,
            "replied_at": s.replied_at
        }
        for s in suggestions
    ]
