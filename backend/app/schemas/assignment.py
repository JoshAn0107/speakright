from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Word Database Schemas
class WordDatabaseBase(BaseModel):
    name: str
    description: Optional[str] = None


class WordDatabaseCreate(WordDatabaseBase):
    pass


class WordDatabaseResponse(WordDatabaseBase):
    id: int
    word_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class WordDatabaseWordBase(BaseModel):
    word_text: str
    definition: Optional[str] = None
    example_sentence: Optional[str] = None
    difficulty_level: Optional[str] = None


class WordDatabaseWordCreate(WordDatabaseWordBase):
    database_id: int


class WordDatabaseWordResponse(WordDatabaseWordBase):
    id: int
    database_id: int

    class Config:
        from_attributes = True


# Assignment Schemas
class AssignmentWordCreate(BaseModel):
    word_text: str


class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    word_database_id: Optional[int] = None
    due_date: Optional[datetime] = None
    words: List[str]  # List of word texts (20-40 words)
    student_ids: List[int]  # List of student IDs to assign to


class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class AssignmentWordResponse(BaseModel):
    id: int
    word_text: str
    order_index: int

    class Config:
        from_attributes = True


class AssignmentStudentResponse(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    assigned_at: datetime
    completed_at: Optional[datetime] = None
    completion_percentage: Optional[float] = None

    class Config:
        from_attributes = True


class AssignmentResponse(BaseModel):
    id: int
    teacher_id: int
    title: str
    description: Optional[str] = None
    word_database_id: Optional[int] = None
    word_database_name: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    words: List[AssignmentWordResponse] = []
    word_count: int
    student_count: int

    class Config:
        from_attributes = True


class StudentAssignmentResponse(BaseModel):
    """Assignment from student's perspective"""
    id: int
    title: str
    description: Optional[str] = None
    teacher_name: Optional[str] = None
    word_database_name: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_at: datetime
    completed_at: Optional[datetime] = None
    words: List[AssignmentWordResponse] = []
    total_words: int
    completed_words: int
    completion_percentage: float
    is_overdue: bool

    class Config:
        from_attributes = True


class AssignmentSubmissionCreate(BaseModel):
    assignment_id: int
    word_text: str
    recording_id: int


class AssignmentSubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    word_text: str
    recording_id: Optional[int] = None
    submitted_at: datetime

    class Config:
        from_attributes = True


class AssignmentProgressResponse(BaseModel):
    """Detailed progress for a specific assignment"""
    assignment: AssignmentResponse
    total_words: int
    completed_words: int
    completion_percentage: float
    word_submissions: List[dict]  # word_text, submitted, recording_id, score

    class Config:
        from_attributes = True
