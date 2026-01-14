"""
Database initialization script
Run this to create all tables
"""

from app.db.session import Base, engine
from app.models.user import User
from app.models.word import WordAssignment
from app.models.recording import Recording
from app.models.classes import Class, ClassEnrollment, Assignment
from app.models.progress import StudentProgress


def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def drop_all():
    """Drop all database tables (use with caution!)"""
    print("WARNING: Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped!")


if __name__ == "__main__":
    init_db()
