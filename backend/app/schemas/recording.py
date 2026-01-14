from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class RecordingCreate(BaseModel):
    """Data for creating a recording"""
    word_text: str
    # Audio file will be uploaded separately via multipart/form-data


class RecordingResponse(BaseModel):
    """Recording with all details"""
    id: int
    student_id: int
    word_text: str
    audio_file_path: str
    automated_scores: Optional[Dict[str, Any]] = None
    teacher_feedback: Optional[str] = None
    teacher_audio_feedback_url: Optional[str] = None
    teacher_grade: Optional[str] = None
    status: str
    flag_for_practice: bool
    is_automated_feedback: bool = True
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TeacherFeedbackCreate(BaseModel):
    """Teacher feedback submission"""
    recording_id: int
    feedback_text: Optional[str] = None
    grade: Optional[str] = None
    flag_for_practice: bool = False


class ProgressResponse(BaseModel):
    """Student progress statistics"""
    words_practiced: int
    average_score: float
    total_attempts: int
    streak_count: int
    recent_recordings: list
