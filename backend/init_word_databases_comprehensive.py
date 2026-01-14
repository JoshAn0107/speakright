"""
Initialize word databases with comprehensive vocabulary lists for IELTS, Zhongkao, and TOEFL
This version includes 100+ words per database
Run this script to update/repopulate word databases
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


# IELTS Academic Vocabulary (100 words)
IELTS_WORDS = [
    # Academic Word List
    {"word": "achieve", "definition": "to successfully complete or reach a goal", "difficulty": "intermediate"},
    {"word": "acquire", "definition": "to gain or obtain something", "difficulty": "intermediate"},
    {"word": "adapt", "definition": "to adjust to new conditions", "difficulty": "intermediate"},
    {"word": "adequate", "definition": "enough or satisfactory for a requirement", "difficulty": "intermediate"},
    {"word": "adjust", "definition": "to change slightly to fit or work better", "difficulty": "intermediate"},
    {"word": "adult", "definition": "a fully grown person", "difficulty": "beginner"},
    {"word": "advocate", "definition": "to publicly support or recommend", "difficulty": "advanced"},
    {"word": "affect", "definition": "to have an influence on", "difficulty": "intermediate"},
    {"word": "alternative", "definition": "another choice or option", "difficulty": "intermediate"},
    {"word": "analyze", "definition": "to examine in detail", "difficulty": "intermediate"},
    {"word": "annual", "definition": "happening once every year", "difficulty": "intermediate"},
    {"word": "anticipate", "definition": "to expect or predict", "difficulty": "advanced"},
    {"word": "apparent", "definition": "clearly visible or understood", "difficulty": "intermediate"},
    {"word": "approach", "definition": "a way of doing something", "difficulty": "intermediate"},
    {"word": "appropriate", "definition": "suitable for a particular purpose", "difficulty": "intermediate"},
    {"word": "approximate", "definition": "close to the actual value", "difficulty": "intermediate"},
    {"word": "area", "definition": "a region or part of a place", "difficulty": "beginner"},
    {"word": "aspect", "definition": "a particular part or feature", "difficulty": "intermediate"},
    {"word": "assess", "definition": "to evaluate or estimate", "difficulty": "intermediate"},
    {"word": "assign", "definition": "to give a task to someone", "difficulty": "intermediate"},
    {"word": "assume", "definition": "to suppose something is true", "difficulty": "intermediate"},
    {"word": "assure", "definition": "to tell someone confidently", "difficulty": "intermediate"},
    {"word": "attach", "definition": "to fasten or join", "difficulty": "intermediate"},
    {"word": "attain", "definition": "to succeed in achieving", "difficulty": "intermediate"},
    {"word": "attitude", "definition": "a way of thinking or feeling", "difficulty": "intermediate"},
    {"word": "attribute", "definition": "a quality or characteristic", "difficulty": "intermediate"},
    {"word": "author", "definition": "a writer of a book or article", "difficulty": "beginner"},
    {"word": "authority", "definition": "the power to give orders", "difficulty": "intermediate"},
    {"word": "available", "definition": "able to be used or obtained", "difficulty": "intermediate"},
    {"word": "aware", "definition": "having knowledge of something", "difficulty": "intermediate"},
    {"word": "behalf", "definition": "in the interest of someone", "difficulty": "intermediate"},
    {"word": "benefit", "definition": "an advantage or profit", "difficulty": "intermediate"},
    {"word": "bias", "definition": "prejudice in favor or against", "difficulty": "advanced"},
    {"word": "bond", "definition": "a connection between people", "difficulty": "intermediate"},
    {"word": "brief", "definition": "lasting only a short time", "difficulty": "intermediate"},
    {"word": "bulk", "definition": "the main or greater part", "difficulty": "intermediate"},
    {"word": "capable", "definition": "having the ability to do", "difficulty": "intermediate"},
    {"word": "capacity", "definition": "the maximum amount that can be contained", "difficulty": "intermediate"},
    {"word": "category", "definition": "a class or division", "difficulty": "intermediate"},
    {"word": "cease", "definition": "to stop or come to an end", "difficulty": "advanced"},
    {"word": "challenge", "definition": "a difficult task", "difficulty": "intermediate"},
    {"word": "channel", "definition": "a means of communication", "difficulty": "intermediate"},
    {"word": "chapter", "definition": "a section of a book", "difficulty": "beginner"},
    {"word": "chart", "definition": "a diagram showing information", "difficulty": "beginner"},
    {"word": "circumstance", "definition": "a fact or condition", "difficulty": "advanced"},
    {"word": "cite", "definition": "to quote as evidence", "difficulty": "intermediate"},
    {"word": "civil", "definition": "relating to citizens", "difficulty": "intermediate"},
    {"word": "clarify", "definition": "to make clear", "difficulty": "intermediate"},
    {"word": "classic", "definition": "judged over time to be of high quality", "difficulty": "intermediate"},
    {"word": "clause", "definition": "a distinct article in a document", "difficulty": "intermediate"},
    {"word": "code", "definition": "a system of rules or symbols", "difficulty": "intermediate"},
    {"word": "coherent", "definition": "logical and consistent", "difficulty": "advanced"},
    {"word": "coincide", "definition": "to occur at the same time", "difficulty": "advanced"},
    {"word": "collapse", "definition": "to fall down suddenly", "difficulty": "intermediate"},
    {"word": "colleague", "definition": "a person you work with", "difficulty": "intermediate"},
    {"word": "commence", "definition": "to begin", "difficulty": "advanced"},
    {"word": "comment", "definition": "a remark expressing opinion", "difficulty": "beginner"},
    {"word": "commission", "definition": "an instruction to create something", "difficulty": "intermediate"},
    {"word": "commit", "definition": "to carry out an action", "difficulty": "intermediate"},
    {"word": "commodity", "definition": "a raw material or product", "difficulty": "intermediate"},
    {"word": "communicate", "definition": "to share information", "difficulty": "intermediate"},
    {"word": "community", "definition": "a group of people living together", "difficulty": "intermediate"},
    {"word": "compatible", "definition": "able to exist together", "difficulty": "advanced"},
    {"word": "compensate", "definition": "to make up for something", "difficulty": "advanced"},
    {"word": "compile", "definition": "to collect and arrange", "difficulty": "intermediate"},
    {"word": "complement", "definition": "something that completes", "difficulty": "advanced"},
    {"word": "complex", "definition": "consisting of many parts", "difficulty": "intermediate"},
    {"word": "component", "definition": "a part of a larger whole", "difficulty": "intermediate"},
    {"word": "compound", "definition": "made up of several parts", "difficulty": "intermediate"},
    {"word": "comprehensive", "definition": "including everything", "difficulty": "intermediate"},
    {"word": "comprise", "definition": "to consist of", "difficulty": "advanced"},
    {"word": "compute", "definition": "to calculate", "difficulty": "intermediate"},
    {"word": "conceive", "definition": "to form an idea", "difficulty": "advanced"},
    {"word": "concentrate", "definition": "to focus attention", "difficulty": "intermediate"},
    {"word": "concept", "definition": "an abstract idea", "difficulty": "intermediate"},
    {"word": "conclude", "definition": "to bring to an end", "difficulty": "intermediate"},
    {"word": "concurrent", "definition": "happening at the same time", "difficulty": "advanced"},
    {"word": "conduct", "definition": "to organize and carry out", "difficulty": "intermediate"},
    {"word": "confer", "definition": "to grant or discuss", "difficulty": "advanced"},
    {"word": "confine", "definition": "to keep within limits", "difficulty": "intermediate"},
    {"word": "confirm", "definition": "to establish truth", "difficulty": "intermediate"},
    {"word": "conflict", "definition": "a serious disagreement", "difficulty": "intermediate"},
    {"word": "conform", "definition": "to comply with rules", "difficulty": "intermediate"},
    {"word": "consent", "definition": "permission or agreement", "difficulty": "intermediate"},
    {"word": "consequent", "definition": "following as a result", "difficulty": "advanced"},
    {"word": "considerable", "definition": "notably large", "difficulty": "intermediate"},
    {"word": "consist", "definition": "to be composed of", "difficulty": "intermediate"},
    {"word": "constant", "definition": "occurring continuously", "difficulty": "intermediate"},
    {"word": "constitute", "definition": "to be a part of a whole", "difficulty": "advanced"},
    {"word": "constrain", "definition": "to restrict or limit", "difficulty": "advanced"},
    {"word": "construct", "definition": "to build or form", "difficulty": "intermediate"},
    {"word": "consult", "definition": "to seek advice from", "difficulty": "intermediate"},
    {"word": "consume", "definition": "to use up", "difficulty": "intermediate"},
    {"word": "contact", "definition": "communication with someone", "difficulty": "beginner"},
    {"word": "contemporary", "definition": "living at the same time", "difficulty": "advanced"},
    {"word": "context", "definition": "the circumstances", "difficulty": "intermediate"},
    {"word": "contract", "definition": "a written agreement", "difficulty": "intermediate"},
    {"word": "contradict", "definition": "to deny or oppose", "difficulty": "advanced"},
    {"word": "contrary", "definition": "opposite in nature", "difficulty": "intermediate"},
    {"word": "contrast", "definition": "to compare differences", "difficulty": "intermediate"},
    {"word": "contribute", "definition": "to give to a common purpose", "difficulty": "intermediate"},
]

# Zhongkao Middle School Vocabulary (100 words)
ZHONGKAO_WORDS = [
    {"word": "ability", "definition": "the power to do something", "difficulty": "beginner"},
    {"word": "aboard", "definition": "on or into a ship or plane", "difficulty": "beginner"},
    {"word": "abroad", "definition": "in or to a foreign country", "difficulty": "beginner"},
    {"word": "absent", "definition": "not present", "difficulty": "beginner"},
    {"word": "accept", "definition": "to receive willingly", "difficulty": "beginner"},
    {"word": "accident", "definition": "an unexpected event", "difficulty": "beginner"},
    {"word": "accurate", "definition": "correct in all details", "difficulty": "intermediate"},
    {"word": "achieve", "definition": "to successfully complete", "difficulty": "intermediate"},
    {"word": "across", "definition": "from one side to the other", "difficulty": "beginner"},
    {"word": "active", "definition": "engaging in action", "difficulty": "beginner"},
    {"word": "actually", "definition": "in fact or really", "difficulty": "intermediate"},
    {"word": "admire", "definition": "to regard with respect", "difficulty": "beginner"},
    {"word": "admit", "definition": "to confess or acknowledge", "difficulty": "intermediate"},
    {"word": "adopt", "definition": "to take up or start to use", "difficulty": "intermediate"},
    {"word": "advanced", "definition": "far on in progress", "difficulty": "intermediate"},
    {"word": "advantage", "definition": "a favorable circumstance", "difficulty": "intermediate"},
    {"word": "adventure", "definition": "an exciting experience", "difficulty": "beginner"},
    {"word": "advice", "definition": "guidance or recommendations", "difficulty": "beginner"},
    {"word": "afford", "definition": "to have enough money for", "difficulty": "intermediate"},
    {"word": "afraid", "definition": "feeling fear", "difficulty": "beginner"},
    {"word": "against", "definition": "in opposition to", "difficulty": "beginner"},
    {"word": "agree", "definition": "to have the same opinion", "difficulty": "beginner"},
    {"word": "ahead", "definition": "in front or forward", "difficulty": "beginner"},
    {"word": "alarm", "definition": "a warning of danger", "difficulty": "beginner"},
    {"word": "allow", "definition": "to give permission", "difficulty": "beginner"},
    {"word": "almost", "definition": "nearly or not quite", "difficulty": "beginner"},
    {"word": "alone", "definition": "by oneself", "difficulty": "beginner"},
    {"word": "although", "definition": "despite the fact that", "difficulty": "intermediate"},
    {"word": "always", "definition": "at all times", "difficulty": "beginner"},
    {"word": "amazing", "definition": "causing great surprise", "difficulty": "beginner"},
    {"word": "among", "definition": "surrounded by", "difficulty": "beginner"},
    {"word": "amount", "definition": "a quantity of something", "difficulty": "intermediate"},
    {"word": "ancient", "definition": "very old", "difficulty": "beginner"},
    {"word": "angry", "definition": "feeling or showing anger", "difficulty": "beginner"},
    {"word": "announce", "definition": "to make known publicly", "difficulty": "intermediate"},
    {"word": "annual", "definition": "happening once a year", "difficulty": "intermediate"},
    {"word": "another", "definition": "one more or different", "difficulty": "beginner"},
    {"word": "anxious", "definition": "worried or nervous", "difficulty": "intermediate"},
    {"word": "apart", "definition": "separated by a distance", "difficulty": "beginner"},
    {"word": "apologize", "definition": "to express regret", "difficulty": "intermediate"},
    {"word": "appear", "definition": "to come into sight", "difficulty": "beginner"},
    {"word": "apply", "definition": "to make a formal request", "difficulty": "intermediate"},
    {"word": "appoint", "definition": "to assign a job to someone", "difficulty": "intermediate"},
    {"word": "appreciate", "definition": "to recognize the value of", "difficulty": "intermediate"},
    {"word": "approach", "definition": "to come near to", "difficulty": "intermediate"},
    {"word": "appropriate", "definition": "suitable for a situation", "difficulty": "intermediate"},
    {"word": "area", "definition": "a region or space", "difficulty": "beginner"},
    {"word": "argue", "definition": "to give reasons for or against", "difficulty": "intermediate"},
    {"word": "arise", "definition": "to come into being", "difficulty": "intermediate"},
    {"word": "arrange", "definition": "to organize or plan", "difficulty": "intermediate"},
    {"word": "arrest", "definition": "to seize by legal authority", "difficulty": "intermediate"},
    {"word": "arrive", "definition": "to reach a destination", "difficulty": "beginner"},
    {"word": "article", "definition": "a piece of writing", "difficulty": "beginner"},
    {"word": "ashamed", "definition": "feeling embarrassed", "difficulty": "intermediate"},
    {"word": "aside", "definition": "to one side", "difficulty": "intermediate"},
    {"word": "asleep", "definition": "in a state of sleep", "difficulty": "beginner"},
    {"word": "aspect", "definition": "a particular part", "difficulty": "intermediate"},
    {"word": "assess", "definition": "to evaluate or estimate", "difficulty": "intermediate"},
    {"word": "assign", "definition": "to allocate a task", "difficulty": "intermediate"},
    {"word": "assist", "definition": "to help", "difficulty": "intermediate"},
    {"word": "assume", "definition": "to suppose to be true", "difficulty": "intermediate"},
    {"word": "astonish", "definition": "to surprise greatly", "difficulty": "intermediate"},
    {"word": "athlete", "definition": "a person who is good at sports", "difficulty": "beginner"},
    {"word": "atmosphere", "definition": "the air in a place", "difficulty": "intermediate"},
    {"word": "attach", "definition": "to fasten or join", "difficulty": "intermediate"},
    {"word": "attack", "definition": "to take aggressive action", "difficulty": "beginner"},
    {"word": "attempt", "definition": "to try to do something", "difficulty": "intermediate"},
    {"word": "attend", "definition": "to be present at", "difficulty": "beginner"},
    {"word": "attention", "definition": "notice or observation", "difficulty": "beginner"},
    {"word": "attitude", "definition": "a way of feeling", "difficulty": "intermediate"},
    {"word": "attract", "definition": "to draw interest", "difficulty": "intermediate"},
    {"word": "audience", "definition": "people watching a performance", "difficulty": "beginner"},
    {"word": "author", "definition": "a writer", "difficulty": "beginner"},
    {"word": "automatic", "definition": "working by itself", "difficulty": "intermediate"},
    {"word": "available", "definition": "able to be used", "difficulty": "intermediate"},
    {"word": "average", "definition": "typical or normal", "difficulty": "intermediate"},
    {"word": "avoid", "definition": "to keep away from", "difficulty": "intermediate"},
    {"word": "awake", "definition": "not sleeping", "difficulty": "beginner"},
    {"word": "award", "definition": "a prize given for achievement", "difficulty": "beginner"},
    {"word": "aware", "definition": "having knowledge of", "difficulty": "intermediate"},
    {"word": "awful", "definition": "very bad", "difficulty": "beginner"},
    {"word": "awkward", "definition": "causing difficulty", "difficulty": "intermediate"},
    {"word": "background", "definition": "the part behind the main focus", "difficulty": "intermediate"},
    {"word": "backward", "definition": "directed behind", "difficulty": "beginner"},
    {"word": "balance", "definition": "an even distribution", "difficulty": "intermediate"},
    {"word": "barely", "definition": "only just", "difficulty": "intermediate"},
    {"word": "bargain", "definition": "something bought cheaply", "difficulty": "intermediate"},
    {"word": "barrier", "definition": "an obstacle", "difficulty": "intermediate"},
    {"word": "basic", "definition": "forming an essential foundation", "difficulty": "intermediate"},
    {"word": "battery", "definition": "a device for storing energy", "difficulty": "beginner"},
    {"word": "battle", "definition": "a fight between armed forces", "difficulty": "beginner"},
    {"word": "behavior", "definition": "the way one acts", "difficulty": "intermediate"},
    {"word": "belief", "definition": "an acceptance that something is true", "difficulty": "intermediate"},
    {"word": "belong", "definition": "to be a member of", "difficulty": "beginner"},
    {"word": "beneath", "definition": "under or below", "difficulty": "intermediate"},
    {"word": "benefit", "definition": "an advantage", "difficulty": "intermediate"},
    {"word": "besides", "definition": "in addition to", "difficulty": "intermediate"},
    {"word": "betray", "definition": "to be disloyal to", "difficulty": "intermediate"},
    {"word": "beyond", "definition": "at or to the further side", "difficulty": "intermediate"},
]

# TOEFL Advanced Academic Vocabulary (100 words)
TOEFL_WORDS = [
    {"word": "abandon", "definition": "to give up completely", "difficulty": "advanced"},
    {"word": "abbreviate", "definition": "to shorten a word or phrase", "difficulty": "advanced"},
    {"word": "abstract", "definition": "existing in thought rather than reality", "difficulty": "advanced"},
    {"word": "absurd", "definition": "wildly unreasonable or illogical", "difficulty": "advanced"},
    {"word": "abundant", "definition": "existing in large quantities", "difficulty": "advanced"},
    {"word": "accelerate", "definition": "to increase speed", "difficulty": "advanced"},
    {"word": "accentuate", "definition": "to make more noticeable", "difficulty": "advanced"},
    {"word": "accessible", "definition": "able to be reached or entered", "difficulty": "advanced"},
    {"word": "accommodate", "definition": "to provide lodging or adapt to", "difficulty": "advanced"},
    {"word": "accomplish", "definition": "to achieve or complete", "difficulty": "advanced"},
    {"word": "accumulate", "definition": "to gather or collect", "difficulty": "advanced"},
    {"word": "accurate", "definition": "correct in all details", "difficulty": "intermediate"},
    {"word": "acknowledge", "definition": "to accept or admit", "difficulty": "advanced"},
    {"word": "acquire", "definition": "to gain possession of", "difficulty": "advanced"},
    {"word": "adapt", "definition": "to adjust to new conditions", "difficulty": "intermediate"},
    {"word": "adequate", "definition": "sufficient for the requirement", "difficulty": "advanced"},
    {"word": "adjacent", "definition": "next to or adjoining", "difficulty": "advanced"},
    {"word": "adjust", "definition": "to alter slightly", "difficulty": "intermediate"},
    {"word": "administer", "definition": "to manage or organize", "difficulty": "advanced"},
    {"word": "admire", "definition": "to regard with respect", "difficulty": "intermediate"},
    {"word": "advocate", "definition": "to publicly recommend", "difficulty": "advanced"},
    {"word": "aesthetic", "definition": "concerned with beauty", "difficulty": "advanced"},
    {"word": "affection", "definition": "a gentle feeling of fondness", "difficulty": "intermediate"},
    {"word": "aggregate", "definition": "a whole formed by combining parts", "difficulty": "advanced"},
    {"word": "aggressive", "definition": "ready to attack", "difficulty": "intermediate"},
    {"word": "aid", "definition": "to help or support", "difficulty": "intermediate"},
    {"word": "allocate", "definition": "to distribute for a purpose", "difficulty": "advanced"},
    {"word": "alter", "definition": "to change or modify", "difficulty": "intermediate"},
    {"word": "alternative", "definition": "one of two or more possibilities", "difficulty": "intermediate"},
    {"word": "ambiguous", "definition": "unclear or having multiple meanings", "difficulty": "advanced"},
    {"word": "ambition", "definition": "a strong desire to achieve", "difficulty": "intermediate"},
    {"word": "amend", "definition": "to make minor changes", "difficulty": "advanced"},
    {"word": "ample", "definition": "enough or more than enough", "difficulty": "advanced"},
    {"word": "analogous", "definition": "comparable in certain respects", "difficulty": "advanced"},
    {"word": "analyze", "definition": "to examine in detail", "difficulty": "intermediate"},
    {"word": "ancient", "definition": "belonging to the very distant past", "difficulty": "beginner"},
    {"word": "animate", "definition": "to bring to life", "difficulty": "advanced"},
    {"word": "annual", "definition": "occurring once every year", "difficulty": "intermediate"},
    {"word": "anomaly", "definition": "something that deviates from normal", "difficulty": "advanced"},
    {"word": "anticipate", "definition": "to expect or predict", "difficulty": "advanced"},
    {"word": "apparent", "definition": "clearly visible or understood", "difficulty": "intermediate"},
    {"word": "append", "definition": "to add to the end", "difficulty": "advanced"},
    {"word": "appreciate", "definition": "to recognize the value", "difficulty": "intermediate"},
    {"word": "approach", "definition": "to come near or nearer to", "difficulty": "intermediate"},
    {"word": "appropriate", "definition": "suitable or proper", "difficulty": "intermediate"},
    {"word": "approximate", "definition": "close to the actual value", "difficulty": "intermediate"},
    {"word": "arbitrary", "definition": "based on random choice", "difficulty": "advanced"},
    {"word": "architecture", "definition": "the art of designing buildings", "difficulty": "intermediate"},
    {"word": "archive", "definition": "a collection of historical documents", "difficulty": "advanced"},
    {"word": "articulate", "definition": "to express clearly", "difficulty": "advanced"},
    {"word": "aspect", "definition": "a particular part or feature", "difficulty": "intermediate"},
    {"word": "aspire", "definition": "to have ambition to achieve", "difficulty": "advanced"},
    {"word": "assemble", "definition": "to gather together", "difficulty": "intermediate"},
    {"word": "assert", "definition": "to state a fact confidently", "difficulty": "advanced"},
    {"word": "assess", "definition": "to evaluate or estimate", "difficulty": "intermediate"},
    {"word": "assign", "definition": "to allocate a task", "difficulty": "intermediate"},
    {"word": "assist", "definition": "to help", "difficulty": "intermediate"},
    {"word": "assume", "definition": "to suppose without proof", "difficulty": "intermediate"},
    {"word": "assure", "definition": "to tell confidently", "difficulty": "intermediate"},
    {"word": "attach", "definition": "to fasten or join", "difficulty": "intermediate"},
    {"word": "attain", "definition": "to achieve or reach", "difficulty": "intermediate"},
    {"word": "attitude", "definition": "a settled way of thinking", "difficulty": "intermediate"},
    {"word": "attribute", "definition": "a quality or characteristic", "difficulty": "intermediate"},
    {"word": "authentic", "definition": "genuine or real", "difficulty": "advanced"},
    {"word": "authority", "definition": "the power to give orders", "difficulty": "intermediate"},
    {"word": "automate", "definition": "to make automatic", "difficulty": "advanced"},
    {"word": "available", "definition": "able to be used", "difficulty": "intermediate"},
    {"word": "aware", "definition": "having knowledge of", "difficulty": "intermediate"},
    {"word": "behalf", "definition": "in the interest of", "difficulty": "intermediate"},
    {"word": "benefit", "definition": "an advantage or profit", "difficulty": "intermediate"},
    {"word": "benevolent", "definition": "well-meaning and kindly", "difficulty": "advanced"},
    {"word": "bias", "definition": "prejudice in favor or against", "difficulty": "advanced"},
    {"word": "bond", "definition": "a connection between people", "difficulty": "intermediate"},
    {"word": "brief", "definition": "of short duration", "difficulty": "intermediate"},
    {"word": "bulk", "definition": "the main or greater part", "difficulty": "intermediate"},
    {"word": "bureaucracy", "definition": "a system of government with complex procedures", "difficulty": "advanced"},
    {"word": "capable", "definition": "having ability or capacity", "difficulty": "intermediate"},
    {"word": "capacity", "definition": "the maximum amount", "difficulty": "intermediate"},
    {"word": "capital", "definition": "wealth in the form of money", "difficulty": "intermediate"},
    {"word": "category", "definition": "a class or division", "difficulty": "intermediate"},
    {"word": "cease", "definition": "to come to an end", "difficulty": "advanced"},
    {"word": "challenge", "definition": "a difficult task", "difficulty": "intermediate"},
    {"word": "channel", "definition": "a means of communication", "difficulty": "intermediate"},
    {"word": "chapter", "definition": "a main division of a book", "difficulty": "beginner"},
    {"word": "characteristic", "definition": "a typical feature", "difficulty": "intermediate"},
    {"word": "chart", "definition": "a diagram showing information", "difficulty": "beginner"},
    {"word": "chronological", "definition": "arranged in order of time", "difficulty": "advanced"},
    {"word": "circulate", "definition": "to move around freely", "difficulty": "advanced"},
    {"word": "circumstance", "definition": "a fact or condition", "difficulty": "advanced"},
    {"word": "cite", "definition": "to quote as evidence", "difficulty": "intermediate"},
    {"word": "civil", "definition": "relating to citizens", "difficulty": "intermediate"},
    {"word": "clarify", "definition": "to make clear", "difficulty": "intermediate"},
    {"word": "classic", "definition": "judged over time to be of high quality", "difficulty": "intermediate"},
    {"word": "classify", "definition": "to arrange in categories", "difficulty": "intermediate"},
    {"word": "clause", "definition": "a unit of grammatical organization", "difficulty": "intermediate"},
    {"word": "coherent", "definition": "logical and consistent", "difficulty": "advanced"},
    {"word": "coincide", "definition": "to occur at the same time", "difficulty": "advanced"},
    {"word": "collaborate", "definition": "to work jointly", "difficulty": "advanced"},
]


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")


def clear_existing_databases(db: Session):
    """Clear existing word databases"""
    print("Clearing existing word databases...")
    db.query(WordDatabaseWord).delete()
    db.query(WordDatabase).delete()
    db.commit()
    print("Existing databases cleared!")


def init_word_databases(db: Session, force_refresh=False):
    """Initialize word databases with comprehensive data"""

    # Check if databases already exist
    existing = db.query(WordDatabase).count()
    if existing > 0 and not force_refresh:
        print(f"Word databases already exist ({existing} found). Use force_refresh=True to repopulate.")
        return

    if existing > 0 and force_refresh:
        clear_existing_databases(db)

    print("Initializing comprehensive word databases...")

    # Create IELTS database
    ielts_db = WordDatabase(
        name="IELTS",
        description="International English Language Testing System vocabulary - Academic Word List",
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
        description="Chinese Middle School English Exam vocabulary - Essential words for grades 7-9",
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
        description="Test of English as a Foreign Language vocabulary - Advanced academic words",
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
    print("=" * 70)
    print("Comprehensive Word Database Initialization Script")
    print("=" * 70)
    print()

    # Create tables
    create_tables()
    print()

    # Initialize databases
    db = SessionLocal()
    try:
        # Set force_refresh=True to repopulate databases
        init_word_databases(db, force_refresh=True)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

    print()
    print("=" * 70)
    print("Initialization complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
