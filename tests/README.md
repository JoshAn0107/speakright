# ILP Pronunciation Portal - Test Suite

This directory contains comprehensive tests for the ILP Pronunciation Portal, organized by testing level according to the L01 Testing Requirements document.

## Test Structure

```
tests/
├── unit/              # Unit tests - Backend logic
│   ├── test_feedback_service.py       # FeedbackService tests
│   ├── test_security.py                # Security functions tests
│   └── test_pronunciation_service.py   # PronunciationService tests
│
├── integration/       # Integration tests - Backend ↔ DB / API
│   ├── test_recording_submission.py    # Recording submission flow
│   └── test_word_assignment.py         # Word assignment integration
│
├── system/            # System tests - Frontend ↔ Backend
│   ├── test_authentication_system.py   # Authentication & RBAC
│   ├── test_student_workflow.py        # Student features
│   └── test_teacher_features.py        # Teacher features
│
├── conftest.py        # Shared fixtures and configuration
├── pytest.ini         # Pytest configuration
└── README.md          # This file
```

## Requirements Mapping

### Unit Tests (12 requirements)
- **test_feedback_service.py**: L01 Requirements 3.a, 3.b, 3.c, 3.i
- **test_security.py**: L01 Requirements 3.d, 3.e, 3.f
- **test_pronunciation_service.py**: L01 Requirements 3.g, 3.h

### Integration Tests (9 requirements)
- **test_recording_submission.py**: L01 Requirements 2.a, 2.e, 2.h
- **test_word_assignment.py**: L01 Requirements 2.d, 2.f, 2.i

### System Tests (13 requirements)
- **test_authentication_system.py**: L01 Requirements 1.a, 1.b
- **test_student_workflow.py**: L01 Requirements 1.c, 1.d, 1.e, 1.f
- **test_teacher_features.py**: L01 Requirements 1.g, 1.i, 1.j, 1.k

## Installation

### Prerequisites

1. Python 3.11+ installed
2. Backend dependencies installed

### Install Test Dependencies

From the project root:

```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-asyncio
```

Optional (for coverage reports):
```bash
pip install pytest-cov
```

## Running Tests

### Run All Tests

From the `tests/` directory:

```bash
cd /root/ilp/tests
pytest
```

### Run Tests by Level

**Unit tests only:**
```bash
pytest unit/
```

**Integration tests only:**
```bash
pytest integration/
```

**System tests only:**
```bash
pytest system/
```

### Run Specific Test Files

```bash
pytest unit/test_feedback_service.py
pytest integration/test_recording_submission.py
pytest system/test_authentication_system.py
```

### Run Specific Test Classes or Functions

```bash
# Run specific test class
pytest unit/test_feedback_service.py::TestCalculateGrade

# Run specific test function
pytest unit/test_feedback_service.py::TestCalculateGrade::test_grade_a_plus_lower_boundary
```

### Verbose Output

```bash
pytest -v
```

### Show Print Statements

```bash
pytest -s
```

### Run with Coverage

```bash
pytest --cov=../backend/app --cov-report=html --cov-report=term
```

Coverage report will be generated in `htmlcov/` directory.

### Run Tests in Parallel (faster)

Install pytest-xdist:
```bash
pip install pytest-xdist
```

Run tests in parallel:
```bash
pytest -n auto
```

## Test Fixtures

The `conftest.py` file provides shared fixtures:

### Database Fixtures
- `test_db`: In-memory SQLite database for each test
- `client`: FastAPI TestClient with database override

### User Fixtures
- `test_student`: Pre-created student user
- `test_teacher`: Pre-created teacher user
- `student_token`: JWT token for student
- `teacher_token`: JWT token for teacher
- `auth_headers_student`: Authorization headers for student
- `auth_headers_teacher`: Authorization headers for teacher

### Recording Fixtures
- `sample_recording`: Sample pronunciation recording
- `sample_word_assignment`: Sample word in database
- `sample_audio_file`: Minimal WAV audio file for testing

### Assessment Fixtures
- `sample_pronunciation_result_excellent`: Mock excellent assessment
- `sample_pronunciation_result_good`: Mock good assessment
- `sample_pronunciation_result_needs_improvement`: Mock needs improvement
- `sample_pronunciation_result_poor`: Mock poor assessment

## Writing New Tests

### Unit Test Example

```python
def test_my_function():
    """Test that my function works correctly"""
    result = my_function(input_data)
    assert result == expected_output
```

### Integration Test Example

```python
def test_database_integration(test_db):
    """Test database operations"""
    # Create record
    record = MyModel(field="value")
    test_db.add(record)
    test_db.commit()

    # Verify
    retrieved = test_db.query(MyModel).first()
    assert retrieved.field == "value"
```

### System Test Example

```python
def test_api_endpoint(client, auth_headers_student):
    """Test complete API workflow"""
    response = client.post(
        "/api/endpoint",
        headers=auth_headers_student,
        json={"data": "value"}
    )

    assert response.status_code == 200
    assert "result" in response.json()
```

## Testing Approaches Used

### Category-Partition Testing
Used for requirements with clear input partitions (e.g., score ranges, status types)

### Pairwise Testing
Used for requirements with multiple independent parameters (e.g., status + class filters)

### Black-box Testing
Used for requirements without natural partitions (e.g., score validation, data joins)

### System Testing
Used for end-to-end verification of system properties (e.g., authentication, performance)

## Common Issues

### Import Errors
If you see import errors, ensure the backend path is in PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:/root/ilp/backend"
```

### Database Errors
The tests use in-memory SQLite, which is created fresh for each test. If you see database errors, ensure SQLAlchemy models are properly imported.

### Async Test Errors
For async tests, ensure pytest-asyncio is installed:
```bash
pip install pytest-asyncio
```

### Audio File Dependencies
Some tests require `pydub` for audio processing:
```bash
pip install pydub
```

## CI/CD Integration

To integrate with CI/CD pipelines:

```bash
# GitHub Actions example
pytest --cov=../backend/app --cov-report=xml --junitxml=junit.xml

# GitLab CI example
pytest --cov=../backend/app --cov-report=term --cov-report=html
```

## Test Coverage Goals

- **Unit tests**: Aim for 90%+ coverage of business logic
- **Integration tests**: Cover all API endpoints and database operations
- **System tests**: Cover all user-facing workflows

## Additional Resources

- [L01 Testing Requirements Document](../L01_Testing_Requirements.md)
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

## Maintenance

When adding new features:
1. Write tests according to L01 requirements document structure
2. Identify the appropriate testing level (unit/integration/system)
3. Choose the appropriate testing approach (category-partition, pairwise, black-box)
4. Document the requirement mapping in test docstrings
5. Update this README if adding new test files or fixtures
