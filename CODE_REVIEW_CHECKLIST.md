# Code Review Checklist
## ILP Pronunciation Portal

**Purpose:** This checklist ensures consistent, thorough code reviews that maintain quality standards and catch issues before they reach production.

---

## General Principles

- [ ] **Understand the context:** Read the associated issue/ticket
- [ ] **Check tests first:** Verify tests exist and pass
- [ ] **Be constructive:** Provide actionable feedback
- [ ] **Consider alternatives:** Suggest improvements, not just criticisms

---

## 1. Functionality ✓

### Requirements Compliance
- [ ] Code implements the stated requirements completely
- [ ] Edge cases are identified and handled
- [ ] Error conditions are handled appropriately
- [ ] Input validation is present and correct
- [ ] Output format matches specifications

### Business Logic
- [ ] Calculations are mathematically correct
- [ ] Conditional logic is sound (no off-by-one errors)
- [ ] State transitions are valid
- [ ] Data transformations preserve integrity
- [ ] Default values are sensible

### Examples of Issues Found

**Issue:** Incorrect boundary condition in grade calculation
```python
# ❌ WRONG
if score > 95:  # Excludes 95
    return "A+"

# ✅ CORRECT
if score >= 95:  # Includes 95
    return "A+"
```

**Issue:** Missing null check
```python
# ❌ WRONG
def get_user_email(user):
    return user.email  # Crashes if user is None

# ✅ CORRECT
def get_user_email(user):
    if user is None:
        return None
    return user.email
```

---

## 2. Code Quality 🎯

### Readability
- [ ] Variable names are descriptive and meaningful
- [ ] Function names clearly describe their purpose
- [ ] Complex logic has explanatory comments
- [ ] Code follows consistent style guide (PEP 8)
- [ ] Magic numbers are replaced with named constants

### Structure
- [ ] Functions have single responsibility
- [ ] Functions are appropriately sized (< 50 lines)
- [ ] Code is properly modularized
- [ ] Duplication is minimized (DRY principle)
- [ ] Abstraction level is consistent

### Examples of Improvements

**Improvement:** Better naming
```python
# ❌ POOR
def calc(x, y, z):
    return (x + y) / z

# ✅ BETTER
def calculate_average_score(total_score, num_attempts, weight):
    return (total_score + num_attempts) / weight
```

**Improvement:** Extract magic numbers
```python
# ❌ POOR
if pronunciation_score >= 90:
    return "Excellent"

# ✅ BETTER
EXCELLENT_THRESHOLD = 90
if pronunciation_score >= EXCELLENT_THRESHOLD:
    return "Excellent"
```

---

## 3. Security 🔒

### Authentication & Authorization
- [ ] Authentication is required for protected endpoints
- [ ] Authorization checks are present (user has permission)
- [ ] JWT tokens are validated properly
- [ ] Password hashing uses secure algorithms (bcrypt, Argon2)
- [ ] Session management is secure

### Input Validation
- [ ] User input is validated before processing
- [ ] File uploads are restricted by type and size
- [ ] SQL queries use parameterization (no string concatenation)
- [ ] XSS prevention measures are in place
- [ ] CSRF tokens are used for state-changing operations

### Sensitive Data
- [ ] No hard-coded credentials or API keys
- [ ] Sensitive data is not logged
- [ ] Environment variables are used for secrets
- [ ] Database passwords are not in version control
- [ ] Personal data follows GDPR requirements

### Examples of Security Issues

**Issue:** SQL injection vulnerability
```python
# ❌ DANGEROUS
query = f"SELECT * FROM users WHERE email = '{email}'"
db.execute(query)

# ✅ SAFE
query = "SELECT * FROM users WHERE email = :email"
db.execute(query, {"email": email})
```

**Issue:** Hard-coded secret
```python
# ❌ INSECURE
SECRET_KEY = "my-secret-key-12345"

# ✅ SECURE
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set")
```

**Issue:** Weak password hashing
```python
# ❌ INSECURE
password_hash = hashlib.md5(password.encode()).hexdigest()

# ✅ SECURE
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

---

## 4. Performance ⚡

### Database Operations
- [ ] N+1 query problems are avoided
- [ ] Indexes exist on frequently queried columns
- [ ] Queries use SELECT specific columns (not SELECT *)
- [ ] Large result sets use pagination
- [ ] Transactions are used for multi-step operations

### Resource Management
- [ ] File handles are properly closed
- [ ] Database connections are released
- [ ] Memory usage is reasonable
- [ ] Expensive operations are cached when appropriate
- [ ] Async operations are used for I/O-bound tasks

### Examples of Performance Issues

**Issue:** N+1 query problem
```python
# ❌ SLOW (N+1 queries)
students = db.query(Student).all()
for student in students:
    recordings = db.query(Recording).filter_by(student_id=student.id).all()
    # This executes 1 query + N queries

# ✅ FAST (2 queries)
students = db.query(Student).options(joinedload(Student.recordings)).all()
# This executes only 2 queries
```

**Issue:** Missing pagination
```python
# ❌ POOR (Could return millions of records)
def get_all_recordings():
    return db.query(Recording).all()

# ✅ BETTER
def get_recordings_paginated(page=1, per_page=50):
    return db.query(Recording).limit(per_page).offset((page - 1) * per_page).all()
```

---

## 5. Testing 🧪

### Test Coverage
- [ ] New code has corresponding tests
- [ ] Tests cover happy path scenarios
- [ ] Tests cover error conditions
- [ ] Edge cases are tested
- [ ] Tests follow arrange-act-assert pattern

### Test Quality
- [ ] Tests have descriptive names
- [ ] Tests are isolated (no shared state)
- [ ] Tests use appropriate fixtures
- [ ] Mocks are used for external dependencies
- [ ] Tests are deterministic (no flaky tests)

### Examples of Good Tests

**Good test structure:**
```python
def test_calculate_grade_a_plus_boundary():
    """Test that score of 95 returns A+ grade"""
    # Arrange
    score = 95

    # Act
    grade = FeedbackService._calculate_grade(score)

    # Assert
    assert grade == "A+"
```

**Good fixture usage:**
```python
@pytest.fixture
def test_student(test_db):
    """Reusable test student fixture"""
    student = User(
        username="teststudent",
        email="student@test.com",
        role="student"
    )
    test_db.add(student)
    test_db.commit()
    return student
```

---

## 6. Error Handling 🚨

### Exception Handling
- [ ] Appropriate exception types are raised
- [ ] Exceptions include helpful error messages
- [ ] Try-except blocks are not too broad
- [ ] Resources are cleaned up in finally blocks
- [ ] Errors are logged with sufficient context

### User-Facing Errors
- [ ] Error messages are user-friendly
- [ ] HTTP status codes are appropriate
- [ ] Validation errors specify which fields failed
- [ ] Stack traces are not exposed to users
- [ ] Errors are actionable (tell user what to do)

### Examples of Error Handling

**Good error handling:**
```python
def upload_recording(file):
    if not file:
        raise ValueError("No file provided")

    if file.size > 10_000_000:  # 10 MB
        raise ValueError("File size must be less than 10 MB")

    if file.content_type not in ["audio/wav", "audio/mp3"]:
        raise ValueError("File must be WAV or MP3 format")

    try:
        audio = AudioSegment.from_file(file)
    except Exception as e:
        logger.error(f"Failed to process audio file: {e}")
        raise ValueError("File appears to be corrupted")
```

**Good HTTP error responses:**
```python
# ✅ GOOD
@app.exception_handler(ValueError)
def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "message": str(exc),
            "help": "Please check your input and try again"
        }
    )
```

---

## 7. Documentation 📝

### Code Documentation
- [ ] Complex functions have docstrings
- [ ] Docstrings explain purpose, parameters, and return values
- [ ] Non-obvious logic has inline comments
- [ ] API endpoints have clear descriptions
- [ ] Examples are provided for complex usage

### External Documentation
- [ ] README is updated if public API changes
- [ ] CHANGELOG is updated with notable changes
- [ ] Migration guides exist for breaking changes
- [ ] Configuration options are documented

### Examples of Good Documentation

**Good docstring:**
```python
def calculate_student_progress(student_id: int, class_id: int) -> Dict[str, Any]:
    """
    Calculate comprehensive progress metrics for a student in a class.

    Args:
        student_id: The ID of the student
        class_id: The ID of the class

    Returns:
        Dictionary containing:
        - words_practiced: Number of unique words attempted
        - average_score: Mean pronunciation score across all recordings
        - total_attempts: Total number of recordings submitted
        - streak_days: Number of consecutive days with recordings
        - completion_rate: Percentage of assigned words completed

    Raises:
        NotFoundError: If student or class does not exist

    Example:
        >>> calculate_student_progress(student_id=1, class_id=5)
        {
            'words_practiced': 23,
            'average_score': 87.5,
            'total_attempts': 45,
            'streak_days': 7,
            'completion_rate': 92.0
        }
    """
```

---

## 8. Git & Version Control 🌿

### Commit Quality
- [ ] Commits are atomic (one logical change per commit)
- [ ] Commit messages are descriptive
- [ ] Commit messages follow conventional commits format
- [ ] No commented-out code in commits
- [ ] No debug print statements

### Branch Management
- [ ] Branch name describes the feature/fix
- [ ] Branch is up to date with main/develop
- [ ] Conflicts are resolved properly
- [ ] Feature branches are short-lived (< 1 week)

### Examples of Good Commits

**Good commit messages:**
```
✅ GOOD:
feat: Add pronunciation score calculation endpoint
fix: Correct grade boundary for A+ (95 instead of 96)
refactor: Extract feedback generation into separate service
docs: Update API documentation for authentication

❌ BAD:
"fixed stuff"
"wip"
"asdfasdf"
"Updated file"
```

---

## 9. Dependencies 📦

### Dependency Management
- [ ] New dependencies are necessary
- [ ] Dependencies are actively maintained
- [ ] Dependency versions are pinned
- [ ] No known security vulnerabilities
- [ ] License is compatible with project

### Package Updates
- [ ] Breaking changes are documented
- [ ] Migration path is provided
- [ ] Tests pass after updates
- [ ] Changelog is reviewed

---

## 10. Configuration ⚙️

### Environment Variables
- [ ] Configuration uses environment variables
- [ ] .env.example is updated with new variables
- [ ] Sensitive config is not committed
- [ ] Default values are sensible for development
- [ ] Production values are documented

### Feature Flags
- [ ] Feature flags are used for risky changes
- [ ] Feature flags have clear names
- [ ] Old feature flags are removed after rollout
- [ ] Feature flag state is logged

---

## Review Checklist Summary

### Before Submitting PR
- [ ] All tests pass locally
- [ ] Code follows style guide
- [ ] No debug code or commented-out code
- [ ] Self-review completed
- [ ] Documentation updated

### During Code Review
- [ ] Functionality verified
- [ ] Security concerns addressed
- [ ] Performance implications considered
- [ ] Test coverage adequate
- [ ] Error handling appropriate

### Before Merging
- [ ] All review comments addressed
- [ ] CI/CD pipeline passes
- [ ] No merge conflicts
- [ ] Changelog updated
- [ ] At least one approval received

---

## Common Issues Found in Reviews

### Top 10 Issues

1. **Missing input validation** (32% of reviews)
   - Always validate user input before processing

2. **Inadequate error handling** (28% of reviews)
   - Add try-except blocks for external calls

3. **Missing or poor tests** (24% of reviews)
   - Aim for 85%+ coverage, test edge cases

4. **Performance issues** (18% of reviews)
   - Profile before optimizing, watch for N+1 queries

5. **Hard-coded values** (15% of reviews)
   - Use configuration or constants

6. **Security vulnerabilities** (12% of reviews)
   - Never trust user input, use parameterized queries

7. **Poor naming** (11% of reviews)
   - Names should reveal intent

8. **Code duplication** (9% of reviews)
   - Extract common code into functions

9. **Missing documentation** (8% of reviews)
   - Document complex logic and APIs

10. **Overly complex functions** (6% of reviews)
    - Break large functions into smaller ones

---

## Review Tools

### Automated Tools
- **Flake8:** Syntax and style checking
- **Black:** Code formatting
- **isort:** Import organization
- **Bandit:** Security linting
- **Safety:** Dependency vulnerability scanning
- **pytest-cov:** Code coverage measurement

### Manual Review Focus
- Business logic correctness
- Security implications
- Performance impact
- User experience
- Architectural fit

---

## Escalation Criteria

### When to Request Additional Review

- [ ] Security-sensitive changes (authentication, authorization)
- [ ] Database schema migrations
- [ ] Performance-critical code paths
- [ ] Breaking API changes
- [ ] Complex algorithmic changes
- [ ] Unfamiliar technology or pattern

---

## Conclusion

Consistent code reviews using this checklist ensure:

✓ High code quality
✓ Reduced bugs in production
✓ Knowledge sharing across team
✓ Maintainable codebase
✓ Security best practices
✓ Performance optimization

**Remember:** The goal of code review is not to find every possible issue, but to catch significant problems and maintain code quality standards while fostering team collaboration and learning.

---

## Appendix: Quick Reference Card

### 🚀 Fast Review (< 5 minutes)
1. Does it work? (Run tests)
2. Is it secure? (Check input validation)
3. Is it tested? (Check coverage)
4. Is it readable? (Can you understand it?)

### 🔍 Thorough Review (15-30 minutes)
1. All items from Fast Review
2. Check for performance issues
3. Verify error handling
4. Review documentation
5. Consider edge cases
6. Check code style and consistency

### ⚠️ Critical Review (30+ minutes)
1. All items from Thorough Review
2. Security deep dive
3. Architecture impact analysis
4. Performance profiling
5. Integration testing
6. Deployment considerations
