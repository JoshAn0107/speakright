"""
Initialize word databases with sample vocabulary lists for IELTS, Zhongkao, and TOEFL
Run this script after database migration to populate word databases
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, Base, engine
from app.models.assignment import WordDatabase, WordDatabaseWord
# Import all models so SQLAlchemy knows about them
from app.models.user import User
from app.models.recording import Recording
from app.models.word import WordAssignment
from app.models.progress import StudentProgress
from app.models.classes import Class, ClassEnrollment


# Sample word lists (can be expanded later)
IELTS_WORDS = [
    # Common Academic Words
    {"word": "achieve", "definition": "to successfully complete or reach a goal", "difficulty": "intermediate"},
    {"word": "analysis", "definition": "detailed examination of something", "difficulty": "intermediate"},
    {"word": "approach", "definition": "a way of doing something", "difficulty": "intermediate"},
    {"word": "assess", "definition": "to evaluate or estimate the nature, ability, or quality", "difficulty": "intermediate"},
    {"word": "beneficial", "definition": "having a good or useful effect", "difficulty": "intermediate"},
    {"word": "category", "definition": "a class or division of things", "difficulty": "intermediate"},
    {"word": "concept", "definition": "an abstract idea", "difficulty": "intermediate"},
    {"word": "consequence", "definition": "a result or effect of an action", "difficulty": "intermediate"},
    {"word": "considerable", "definition": "notably large in size, amount, or extent", "difficulty": "intermediate"},
    {"word": "context", "definition": "the circumstances that form the setting", "difficulty": "intermediate"},
    {"word": "demonstrate", "definition": "to show clearly by giving proof", "difficulty": "intermediate"},
    {"word": "diverse", "definition": "showing a great deal of variety", "difficulty": "intermediate"},
    {"word": "economy", "definition": "the system of trade and industry", "difficulty": "intermediate"},
    {"word": "environment", "definition": "the surroundings or conditions", "difficulty": "intermediate"},
    {"word": "evidence", "definition": "information showing whether something is true", "difficulty": "intermediate"},
    {"word": "factor", "definition": "an element that contributes to a result", "difficulty": "intermediate"},
    {"word": "function", "definition": "the purpose or role of something", "difficulty": "intermediate"},
    {"word": "impact", "definition": "a marked effect or influence", "difficulty": "intermediate"},
    {"word": "individual", "definition": "a single person or thing", "difficulty": "intermediate"},
    {"word": "interpret", "definition": "to explain the meaning of", "difficulty": "intermediate"},
    {"word": "maintain", "definition": "to keep in good condition", "difficulty": "intermediate"},
    {"word": "method", "definition": "a particular way of doing something", "difficulty": "intermediate"},
    {"word": "obtain", "definition": "to get or acquire", "difficulty": "intermediate"},
    {"word": "perceive", "definition": "to become aware or conscious of", "difficulty": "intermediate"},
    {"word": "principle", "definition": "a fundamental truth or law", "difficulty": "intermediate"},
    {"word": "process", "definition": "a series of actions or steps", "difficulty": "intermediate"},
    {"word": "relevant", "definition": "closely connected or appropriate", "difficulty": "intermediate"},
    {"word": "require", "definition": "to need for a particular purpose", "difficulty": "intermediate"},
    {"word": "significant", "definition": "sufficiently great or important", "difficulty": "intermediate"},
    {"word": "structure", "definition": "the arrangement of parts", "difficulty": "intermediate"},
]

ZHONGKAO_WORDS = [
    # Common Chinese Middle School English Words
    {"word": "abroad", "definition": "in or to a foreign country", "difficulty": "beginner"},
    {"word": "accept", "definition": "to receive willingly", "difficulty": "beginner"},
    {"word": "accident", "definition": "an unexpected event", "difficulty": "beginner"},
    {"word": "achieve", "definition": "to successfully complete", "difficulty": "intermediate"},
    {"word": "advice", "definition": "guidance or recommendations", "difficulty": "beginner"},
    {"word": "agree", "definition": "to have the same opinion", "difficulty": "beginner"},
    {"word": "allow", "definition": "to give permission", "difficulty": "beginner"},
    {"word": "although", "definition": "in spite of the fact that", "difficulty": "intermediate"},
    {"word": "ancient", "definition": "very old", "difficulty": "beginner"},
    {"word": "anxious", "definition": "worried or nervous", "difficulty": "intermediate"},
    {"word": "appear", "definition": "to come into sight", "difficulty": "beginner"},
    {"word": "arrange", "definition": "to organize or plan", "difficulty": "intermediate"},
    {"word": "attend", "definition": "to be present at", "difficulty": "beginner"},
    {"word": "attract", "definition": "to draw interest or attention", "difficulty": "intermediate"},
    {"word": "average", "definition": "typical or normal", "difficulty": "intermediate"},
    {"word": "avoid", "definition": "to keep away from", "difficulty": "intermediate"},
    {"word": "awake", "definition": "not sleeping", "difficulty": "beginner"},
    {"word": "balance", "definition": "an even distribution", "difficulty": "intermediate"},
    {"word": "behavior", "definition": "the way one acts", "difficulty": "intermediate"},
    {"word": "believe", "definition": "to accept as true", "difficulty": "beginner"},
    {"word": "benefit", "definition": "an advantage or profit", "difficulty": "intermediate"},
    {"word": "brave", "definition": "showing courage", "difficulty": "beginner"},
    {"word": "bright", "definition": "giving out much light", "difficulty": "beginner"},
    {"word": "celebrate", "definition": "to mark a special occasion", "difficulty": "beginner"},
    {"word": "century", "definition": "a period of one hundred years", "difficulty": "beginner"},
    {"word": "challenge", "definition": "a difficult task", "difficulty": "intermediate"},
    {"word": "character", "definition": "the qualities of a person", "difficulty": "intermediate"},
    {"word": "cheerful", "definition": "happy and positive", "difficulty": "beginner"},
    {"word": "climate", "definition": "the weather conditions", "difficulty": "intermediate"},
    {"word": "comfortable", "definition": "providing ease and relaxation", "difficulty": "beginner"},
]

TOEFL_WORDS = [
    # Advanced Academic Words for TOEFL
    {"word": "abandon", "definition": "to give up completely", "difficulty": "advanced"},
    {"word": "abstract", "definition": "existing in thought or as an idea", "difficulty": "advanced"},
    {"word": "accommodate", "definition": "to provide lodging or adapt to", "difficulty": "advanced"},
    {"word": "accumulate", "definition": "to gather or collect", "difficulty": "advanced"},
    {"word": "adequate", "definition": "sufficient for the requirement", "difficulty": "advanced"},
    {"word": "adjacent", "definition": "next to or adjoining", "difficulty": "advanced"},
    {"word": "advocate", "definition": "to publicly recommend or support", "difficulty": "advanced"},
    {"word": "aggregate", "definition": "a whole formed by combining parts", "difficulty": "advanced"},
    {"word": "allocate", "definition": "to distribute for a purpose", "difficulty": "advanced"},
    {"word": "ambiguous", "definition": "unclear or having multiple meanings", "difficulty": "advanced"},
    {"word": "analogous", "definition": "comparable in certain respects", "difficulty": "advanced"},
    {"word": "anticipate", "definition": "to expect or predict", "difficulty": "advanced"},
    {"word": "arbitrary", "definition": "based on random choice", "difficulty": "advanced"},
    {"word": "authenticate", "definition": "to prove something is genuine", "difficulty": "advanced"},
    {"word": "capability", "definition": "the power or ability to do something", "difficulty": "advanced"},
    {"word": "circumstance", "definition": "a fact or condition connected with an event", "difficulty": "advanced"},
    {"word": "coherent", "definition": "logical and consistent", "difficulty": "advanced"},
    {"word": "coincide", "definition": "to occur at the same time", "difficulty": "advanced"},
    {"word": "commence", "definition": "to begin or start", "difficulty": "advanced"},
    {"word": "compatible", "definition": "able to exist together", "difficulty": "advanced"},
    {"word": "compensate", "definition": "to make up for something", "difficulty": "advanced"},
    {"word": "complement", "definition": "something that completes", "difficulty": "advanced"},
    {"word": "comprise", "definition": "to consist of or be made up of", "difficulty": "advanced"},
    {"word": "conceive", "definition": "to form an idea or plan", "difficulty": "advanced"},
    {"word": "contemporary", "definition": "existing at the same time", "difficulty": "advanced"},
    {"word": "contradict", "definition": "to deny or oppose", "difficulty": "advanced"},
    {"word": "crucial", "definition": "of great importance", "difficulty": "advanced"},
    {"word": "diminish", "definition": "to make or become less", "difficulty": "advanced"},
    {"word": "distribute", "definition": "to give out or spread", "difficulty": "advanced"},
    {"word": "emphasis", "definition": "special importance given to something", "difficulty": "advanced"},
]


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")


def init_word_databases(db: Session):
    """Initialize word databases with sample data"""

    # Check if databases already exist
    existing = db.query(WordDatabase).count()
    if existing > 0:
        print(f"Word databases already exist ({existing} found). Skipping initialization.")
        return

    print("Initializing word databases...")

    # Create IELTS database
    ielts_db = WordDatabase(
        name="IELTS",
        description="International English Language Testing System vocabulary",
        word_count=len(IELTS_WORDS)
    )
    db.add(ielts_db)
    db.flush()

    for word_data in IELTS_WORDS:
        word = WordDatabaseWord(
            database_id=ielts_db.id,
            word_text=word_data["word"],
            definition=word_data["definition"],
            difficulty_level=word_data["difficulty"]
        )
        db.add(word)

    print(f"✓ Created IELTS database with {len(IELTS_WORDS)} words")

    # Create Zhongkao database
    zhongkao_db = WordDatabase(
        name="Zhongkao",
        description="Chinese Middle School English Exam vocabulary",
        word_count=len(ZHONGKAO_WORDS)
    )
    db.add(zhongkao_db)
    db.flush()

    for word_data in ZHONGKAO_WORDS:
        word = WordDatabaseWord(
            database_id=zhongkao_db.id,
            word_text=word_data["word"],
            definition=word_data["definition"],
            difficulty_level=word_data["difficulty"]
        )
        db.add(word)

    print(f"✓ Created Zhongkao database with {len(ZHONGKAO_WORDS)} words")

    # Create TOEFL database
    toefl_db = WordDatabase(
        name="TOEFL",
        description="Test of English as a Foreign Language vocabulary",
        word_count=len(TOEFL_WORDS)
    )
    db.add(toefl_db)
    db.flush()

    for word_data in TOEFL_WORDS:
        word = WordDatabaseWord(
            database_id=toefl_db.id,
            word_text=word_data["word"],
            definition=word_data["definition"],
            difficulty_level=word_data["difficulty"]
        )
        db.add(word)

    print(f"✓ Created TOEFL database with {len(TOEFL_WORDS)} words")

    db.commit()
    print("\n✅ Word databases initialized successfully!")
    print(f"   Total: {len(IELTS_WORDS) + len(ZHONGKAO_WORDS) + len(TOEFL_WORDS)} words across 3 databases")


def main():
    """Main initialization function"""
    print("=" * 60)
    print("Word Database Initialization Script")
    print("=" * 60)
    print()

    # Create tables
    create_tables()
    print()

    # Initialize databases
    db = SessionLocal()
    try:
        init_word_databases(db)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

    print()
    print("=" * 60)
    print("Initialization complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
