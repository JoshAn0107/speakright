# LO4: Design, Justify, and Apply Testing Strategies
## ILP Pronunciation Portal

**Student:** AnJiang
**Email:** anjiang0107@gmail.com
**Repository:** https://github.com/JoshAn0107/speakright
**Date:** 2026-01-17

---

## 4.1 System Context

### Architecture Overview

The ILP Pronunciation Portal is a web-based English pronunciation learning system with:

- **Backend:** FastAPI REST API with PostgreSQL database
- **Frontend:** React single-page application
- **External Services:** Azure Speech API for pronunciation assessment, Dictionary API for word definitions

### Primary Risks

| Risk | Impact | Likelihood |
|------|--------|------------|
| Incorrect grade calculation | High - affects student assessment | Medium |
| Authentication bypass | Critical - security breach | Low |
| Data corruption on recording submission | High - loss of student work | Medium |
| External API failure | Medium - degraded functionality | Medium |

### Users

- **Students:** Submit audio recordings, view feedback and progress
- **Teachers:** Review submissions, override grades, view analytics

---

## 4.2 Testing Levels and Scope

### 4.2.1 Unit Testing

**Scope:** Backend service functions and pure business logic

**Target Components:**
- `FeedbackService._calculate_grade()` - Grade calculation
- `FeedbackService.generate_feedback()` - Feedback text generation
- `verify_password()` / `get_password_hash()` - Security functions
- `create_access_token()` - JWT generation

**Rationale:** These functions contain deterministic business logic that can be tested in isolation without database or network dependencies. Bugs here propagate to all users.

**Test Count:** 103 unit tests

---

### 4.2.2 Integration Testing

**Scope:** API endpoints interacting with database and services

**Target Components:**
- Recording submission → Pronunciation service → Feedback service → Database
- Word assignment creation → Dictionary API → Database
- Progress calculation → Multi-table aggregation

**Rationale:** Integration points are where data transformation errors and transaction failures occur. Testing these paths validates that components work together correctly.

**Test Count:** 23 integration tests

---

### 4.2.3 System Testing

**Scope:** End-to-end user workflows through the deployed API

**Target Workflows:**
- Student: Register → Login → Submit recording → View feedback
- Teacher: Login → View submissions → Provide feedback
- Authentication: All credential and token combinations

**Rationale:** System tests validate that the complete application works from a user's perspective. They catch integration issues that unit and integration tests miss.

**Test Count:** 55 system tests

---

## 4.3 Test Prioritisation and Risk

### Risk-Based Allocation

Testing effort is allocated proportionally to risk and testability:

| Component | Risk Level | Testability | Testing Depth | Rationale |
|-----------|------------|-------------|---------------|-----------|
| **Grade Calculation** | High | High | Exhaustive | Affects all student assessments; pure function |
| **Authentication** | Critical | High | Comprehensive | Security boundary; deterministic |
| **Feedback Generation** | High | High | Thorough | User-facing; business logic |
| **Recording Submission** | High | Medium | Integration focus | Data integrity; multi-step |
| **Teacher Analytics** | Medium | Low | Basic | Secondary feature; complex queries |
| **Frontend UI** | Low | Low | Manual only | Cosmetic; high maintenance cost |

### What Is Tested Heavily

1. **Backend business logic** (FeedbackService, security functions)
   - 100% statement coverage
   - Boundary value analysis on all thresholds
   - Every grade partition tested

2. **Authentication flows**
   - All credential combinations (valid, invalid, missing, malformed)
   - Token validation (valid, expired, tampered)
   - Role-based access control boundaries

3. **Data integrity paths**
   - Recording submission with database transaction
   - Multi-table updates (recordings + word_assignments + progress)

### What Is Tested Lightly

1. **Frontend components**
   - No automated React component tests
   - Reason: High maintenance cost, low business logic, TypeScript provides compile-time safety

2. **External API integrations**
   - Mocked in tests, not tested against real services
   - Reason: Cost, rate limits, non-determinism

3. **Administrative functions**
   - Basic happy-path only
   - Reason: Low usage frequency, manual recovery possible

### Justification

This prioritisation follows the principle of **risk-based testing**: allocate testing effort where failures have the highest impact and bugs are most likely. Backend business logic is both high-risk and highly testable, making it the optimal investment. Frontend testing has diminishing returns due to high maintenance costs and the availability of alternative validation methods (TypeScript, manual testing).

---

## 4.4 Test Environment and Tooling

### Framework Selection

| Tool | Purpose | Rationale |
|------|---------|-----------|
| **pytest** | Test execution | Lightweight syntax, excellent fixture support, pytest-cov integration |
| **pytest-cov** | Coverage measurement | Industry standard, integrates with CI |
| **FastAPI TestClient** | API testing | Built-in, no additional dependencies |
| **SQLite in-memory** | Test database | Fast, isolated, no setup required |

### Why pytest Over Alternatives

- **vs unittest:** Less boilerplate, better fixture management, clearer assertions
- **vs nose:** pytest is actively maintained, better plugin ecosystem
- **vs Robot Framework:** Overkill for API testing, pytest sufficient for our needs

### Test Isolation Strategy

Each test receives:
- Fresh in-memory database (no shared state)
- Dependency-injected test client
- Isolated fixtures with automatic cleanup

This ensures tests are deterministic and can run in any order.

---

## 4.5 Evidence of Application

### Directory Structure Reflects Strategy

```
tests/
├── conftest.py          # Shared fixtures (378 lines)
├── unit/                # 103 tests - business logic isolation
│   ├── test_feedback_service.py
│   ├── test_security.py
│   └── test_pronunciation_service.py
├── integration/         # 23 tests - service interactions
│   ├── test_recording_submission.py
│   └── test_word_assignment.py
└── system/              # 55 tests - end-to-end workflows
    ├── test_authentication_system.py
    ├── test_student_workflow.py
    └── test_teacher_features.py
```

### Test Distribution Matches Risk Assessment

| Level | Tests | % of Total | Matches Strategy |
|-------|-------|------------|------------------|
| Unit | 103 | 57% | ✅ Highest priority (business logic) |
| Integration | 23 | 13% | ✅ Critical touchpoints |
| System | 55 | 30% | ✅ User workflow validation |

### Coverage Reflects Prioritisation

| Component | Coverage | Priority | Match |
|-----------|----------|----------|-------|
| FeedbackService | 100% | High | ✅ |
| Security | 93% | Critical | ✅ |
| Models/Schemas | 100% | High | ✅ |
| Teacher routes | 60% | Medium | ✅ |
| Assignments | 20% | Low | ✅ |

The coverage distribution directly reflects the risk-based prioritisation defined in section 4.3.

---

## 4.6 Connection to CI/CD (LO5)

This testing strategy is operationalised through continuous integration:

```yaml
# .github/workflows/ci-testing.yml
jobs:
  test:
    steps:
      - name: Unit Tests      # Strategy 4.2.1
      - name: Integration Tests  # Strategy 4.2.2
      - name: System Tests    # Strategy 4.2.3
      - name: Coverage Report # Strategy 4.3 validation
```

The CI pipeline enforces this strategy by:
1. Running tests in the defined order (unit → integration → system)
2. Failing fast on unit test failures (highest priority)
3. Generating coverage reports to verify prioritisation
4. Blocking merges if coverage drops below threshold

---

## Summary

### Strategy Design

| Element | Decision |
|---------|----------|
| **Levels** | Unit + Integration + System |
| **Prioritisation** | Risk-based (business logic > UI) |
| **Scope** | Backend comprehensive, frontend manual |
| **Tools** | pytest + pytest-cov + TestClient |

### Strategy Justification

| Decision | Justification |
|----------|---------------|
| Heavy backend testing | High risk, high testability, affects all users |
| Light frontend testing | Low business logic, high maintenance, TypeScript safety |
| Mocked external APIs | Cost, determinism, rate limits |
| In-memory test database | Speed, isolation, no infrastructure |

### Strategy Application

| Evidence | Location |
|----------|----------|
| Test directory structure | `tests/unit/`, `tests/integration/`, `tests/system/` |
| Coverage distribution | 100% on high-priority, 20-60% on low-priority |
| CI pipeline | `.github/workflows/ci-testing.yml` |

**LO4 Assessment:** Testing strategy is clearly designed, justified by risk analysis, and demonstrably applied to the system with evidence in code structure and coverage metrics.

---

**End of LO4 Documentation**
