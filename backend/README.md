# Pronunciation Practice Portal - Backend API

FastAPI-based backend for the English Pronunciation Practice Portal.

## Features

- **User Authentication**: JWT-based auth for students and teachers
- **Dictionary Integration**: Real-time word data from Free Dictionary API
- **Pronunciation Assessment**: Azure Speech Service integration (with mock fallback)
- **Recording Management**: Audio file upload and storage
- **Progress Tracking**: Student performance analytics
- **Teacher Dashboard**: Review submissions and provide feedback

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with passlib
- **External APIs**:
  - Free Dictionary API (no auth required)
  - Azure Speech Service (optional)

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 15+
- (Optional) Azure Speech Service account

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE pronunciation_db;
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE pronunciation_db TO admin;
```

### 4. Environment Configuration

Copy the example env file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
- Set a strong `SECRET_KEY` (generate with: `openssl rand -hex 32`)
- Update `DATABASE_URL` with your database credentials
- (Optional) Add Azure Speech Service credentials

### 5. Initialize Database

Create all tables:

```bash
python -m app.db.init_db
```

### 6. Run the Server

Development mode:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### Words (Public)

- `GET /api/words/{word}` - Get word definition from dictionary
- `GET /api/words/daily/challenge` - Get daily challenge word
- `GET /api/words/topic/{topic}` - Get words by topic
- `GET /api/words/search/{query}` - Search for a word

### Words (Teacher Only)

- `POST /api/words/assign` - Add word to system
- `GET /api/words/assignments/all` - Get all assigned words

### Student Endpoints

- `POST /api/student/recordings/submit` - Submit pronunciation recording
- `GET /api/student/recordings` - Get my recordings
- `GET /api/student/progress` - Get my progress statistics

### Teacher Endpoints

- `GET /api/teacher/submissions` - Get student submissions
- `POST /api/teacher/feedback` - Submit feedback on recording
- `GET /api/teacher/students` - Get student list
- `GET /api/teacher/analytics` - Get analytics and statistics
- `POST /api/teacher/classes` - Create a new class
- `GET /api/teacher/classes` - Get my classes

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Example Usage

### 1. Register a Student

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student1",
    "email": "student1@example.com",
    "password": "password123",
    "role": "student"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student1@example.com",
    "password": "password123"
  }'
```

### 3. Get a Word

```bash
curl http://localhost:8000/api/words/beautiful
```

### 4. Submit Recording (requires auth)

```bash
curl -X POST http://localhost:8000/api/student/recordings/submit \
  -H "Authorization: Bearer <your-token>" \
  -F "word_text=beautiful" \
  -F "audio_file=@recording.wav"
```

## Development Notes

### Mock Pronunciation Assessment

If Azure Speech Service credentials are not configured, the system automatically uses mock data for pronunciation assessment. This allows development and testing without Azure costs.

To enable real pronunciation assessment:
1. Create an Azure Speech Service resource
2. Add `AZURE_SPEECH_KEY` and `AZURE_REGION` to `.env`
3. Restart the server

### Database Migrations

For production, use Alembic for database migrations:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

### File Storage

Audio recordings are stored in the `uploads/` directory, organized by student ID:

```
uploads/
  ├── 1/           # Student ID 1
  │   ├── beautiful_20240101_120000.wav
  │   └── wonderful_20240101_120100.wav
  └── 2/           # Student ID 2
      └── apple_20240101_120200.wav
```

## Testing

Test the API using the interactive documentation at http://localhost:8000/docs

Or use curl/Postman with the examples above.

## Troubleshooting

### Database Connection Error

Check your `DATABASE_URL` in `.env` and ensure PostgreSQL is running:

```bash
psql -U admin -d pronunciation_db
```

### Azure Speech Service Error

If you see Azure-related errors but don't need real pronunciation assessment, the system will fall back to mock data automatically. No action needed.

### CORS Error

Add your frontend URL to `CORS_ORIGINS` in `.env`:

```
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## Production Deployment

For production:

1. Set `DEBUG=False` in `.env`
2. Use a strong `SECRET_KEY`
3. Use a production WSGI server (gunicorn):

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

4. Set up proper database backups
5. Configure file storage (S3/Azure Blob)
6. Use environment variables instead of `.env` file

## License

Educational project for ILP CW3
