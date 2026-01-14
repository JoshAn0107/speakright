from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class WordDatabase(Base):
    """Predefined word databases (IELTS, Zhongkao, TOEFL, etc.)"""
    __tablename__ = "word_databases"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)  # e.g., "IELTS", "Zhongkao", "TOEFL"
    description = Column(Text, nullable=True)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    words = relationship("WordDatabaseWord", back_populates="database", cascade="all, delete-orphan")


class WordDatabaseWord(Base):
    """Words in each word database"""
    __tablename__ = "word_database_words"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    database_id = Column(Integer, ForeignKey("word_databases.id", ondelete="CASCADE"), nullable=False)
    word_text = Column(String(100), nullable=False, index=True)
    definition = Column(Text, nullable=True)
    example_sentence = Column(Text, nullable=True)
    difficulty_level = Column(String(50), nullable=True)  # beginner, intermediate, advanced

    # Relationships
    database = relationship("WordDatabase", back_populates="words")


class Assignment(Base):
    """Teacher-created word assignments"""
    __tablename__ = "assignments"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    word_database_id = Column(Integer, ForeignKey("word_databases.id", ondelete="SET NULL"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    teacher = relationship("User", foreign_keys=[teacher_id])
    words = relationship("AssignmentWord", back_populates="assignment", cascade="all, delete-orphan")
    students = relationship("AssignmentStudent", back_populates="assignment", cascade="all, delete-orphan")
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")


class AssignmentWord(Base):
    """Words included in an assignment (20-40 words per assignment)"""
    __tablename__ = "assignment_words"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    word_text = Column(String(100), nullable=False)
    order_index = Column(Integer, default=0)  # Order of words in the assignment

    # Relationships
    assignment = relationship("Assignment", back_populates="words")


class AssignmentStudent(Base):
    """Which students are assigned which assignments"""
    __tablename__ = "assignment_students"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    assignment = relationship("Assignment", back_populates="students")
    student = relationship("User", foreign_keys=[student_id])


class AssignmentSubmission(Base):
    """Track student progress on assignment words"""
    __tablename__ = "assignment_submissions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    word_text = Column(String(100), nullable=False)
    recording_id = Column(Integer, ForeignKey("recordings.id", ondelete="CASCADE"), nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", foreign_keys=[student_id])
    recording = relationship("Recording", foreign_keys=[recording_id])
