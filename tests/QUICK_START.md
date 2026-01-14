# Quick Start Guide - Running Tests

## 1. Setup (First Time Only)

```bash
# Install dependencies
cd /root/ilp/backend
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov

# Optional: For audio file handling
pip install pydub
```

## 2. Run All Tests

```bash
cd /root/ilp/tests
pytest
```

## 3. Run Tests by Level

```bash
# Unit tests (fastest)
pytest unit/

# Integration tests
pytest integration/

# System tests (slowest, most comprehensive)
pytest system/
```

## 4. Common Commands

```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run specific test file
pytest unit/test_feedback_service.py

# Run specific test class
pytest unit/test_feedback_service.py::TestCalculateGrade

# Run specific test function
pytest unit/test_feedback_service.py::TestCalculateGrade::test_grade_a_plus_lower_boundary

# Run tests matching pattern
pytest -k "authentication"

# Generate coverage report
pytest --cov=../backend/app --cov-report=html
# Then open htmlcov/index.html in browser
```

## 5. Expected Output

```
================================ test session starts =================================
platform linux -- Python 3.12.0, pytest-7.4.3, pluggy-1.3.0
rootdir: /root/ilp/tests
configfile: pytest.ini
testpaths: unit, integration, system
collected 150 items

unit/test_feedback_service.py::TestCalculateGrade::test_grade_a_plus ✓
unit/test_feedback_service.py::TestCalculateGrade::test_grade_a ✓
...
================================ 150 passed in 12.34s =================================
```

## 6. Troubleshooting

### Import Errors
```bash
export PYTHONPATH="${PYTHONPATH}:/root/ilp/backend"
```

### Database Errors
Tests use in-memory SQLite - no setup needed. If errors persist, check SQLAlchemy models.

### Async Errors
```bash
pip install pytest-asyncio
```

## 7. Test Organization

- **Unit tests** (`unit/`): Test individual functions in isolation
- **Integration tests** (`integration/`): Test backend ↔ database/API interactions
- **System tests** (`system/`): Test complete frontend ↔ backend workflows

## 8. Writing New Tests

1. Choose appropriate test level (unit/integration/system)
2. Use fixtures from `conftest.py`
3. Follow naming convention: `test_*.py`, `Test*`, `test_*`
4. Add L01 requirement reference in docstring

Example:
```python
def test_my_feature(client, auth_headers_student):
    """
    L01 Requirement X.Y: Description

    Testing approach: Category-partition testing
    """
    # Arrange
    data = {"field": "value"}

    # Act
    response = client.post("/api/endpoint", json=data, headers=auth_headers_student)

    # Assert
    assert response.status_code == 200
    assert response.json()["result"] == "expected"
```

## 9. CI/CD Integration

```bash
# For continuous integration
pytest --junitxml=junit.xml --cov=../backend/app --cov-report=xml
```

## 10. Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [TEST_COVERAGE_SUMMARY.md](TEST_COVERAGE_SUMMARY.md) for requirement mapping
- Review [L01_Testing_Requirements.md](../L01_Testing_Requirements.md) for testing rationale
