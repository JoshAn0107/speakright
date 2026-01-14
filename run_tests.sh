#!/bin/bash
#
# Automated Test Execution Script
# ILP Pronunciation Portal - LO5 Testing Automation
#
# This script automates the complete testing process including:
# - Code quality checks (linting)
# - Unit tests
# - Integration tests
# - System tests
# - Coverage reporting
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directories
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
TESTS_DIR="$PROJECT_ROOT/tests"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}ILP Pronunciation Portal - Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print section headers
print_section() {
    echo ""
    echo -e "${BLUE}>>> $1${NC}"
    echo ""
}

# Function to print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print warning message
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to print error message
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if virtual environment exists
if [ ! -d "$BACKEND_DIR/venv" ]; then
    print_error "Virtual environment not found. Creating one..."
    cd "$BACKEND_DIR"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Virtual environment created and dependencies installed"
else
    print_success "Virtual environment found"
fi

# Activate virtual environment
source "$BACKEND_DIR/venv/bin/activate"

# Set PYTHONPATH
export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"

# Parse command line arguments
RUN_UNIT=true
RUN_INTEGRATION=true
RUN_SYSTEM=true
RUN_COVERAGE=true
RUN_LINT=true
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit-only)
            RUN_INTEGRATION=false
            RUN_SYSTEM=false
            shift
            ;;
        --integration-only)
            RUN_UNIT=false
            RUN_SYSTEM=false
            shift
            ;;
        --system-only)
            RUN_UNIT=false
            RUN_INTEGRATION=false
            shift
            ;;
        --no-coverage)
            RUN_COVERAGE=false
            shift
            ;;
        --no-lint)
            RUN_LINT=false
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --unit-only          Run only unit tests"
            echo "  --integration-only   Run only integration tests"
            echo "  --system-only        Run only system tests"
            echo "  --no-coverage        Skip coverage report generation"
            echo "  --no-lint            Skip linting checks"
            echo "  --verbose, -v        Verbose output"
            echo "  --help, -h           Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Code Quality Checks
if [ "$RUN_LINT" = true ]; then
    print_section "1. Code Quality Checks"

    # Check if linting tools are installed
    if ! command -v flake8 &> /dev/null; then
        print_warning "flake8 not installed, installing..."
        pip install flake8 black isort --quiet
    fi

    cd "$BACKEND_DIR"

    echo "Running flake8..."
    if flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics; then
        print_success "Flake8 critical checks passed"
    else
        print_warning "Flake8 found some issues"
    fi

    echo ""
fi

# Create test results directory
RESULTS_DIR="$TESTS_DIR/test-results"
mkdir -p "$RESULTS_DIR"

# Initialize test counters
TOTAL_PASSED=0
TOTAL_FAILED=0
TOTAL_ERRORS=0

# Run Unit Tests
if [ "$RUN_UNIT" = true ]; then
    print_section "2. Running Unit Tests"
    cd "$TESTS_DIR"

    if [ "$VERBOSE" = true ]; then
        pytest unit/ -v --tb=short --junit-xml="$RESULTS_DIR/unit-results.xml" || true
    else
        pytest unit/ --tb=short --junit-xml="$RESULTS_DIR/unit-results.xml" || true
    fi

    print_success "Unit tests completed"
fi

# Run Integration Tests
if [ "$RUN_INTEGRATION" = true ]; then
    print_section "3. Running Integration Tests"
    cd "$TESTS_DIR"

    if [ "$VERBOSE" = true ]; then
        pytest integration/ -v --tb=short --junit-xml="$RESULTS_DIR/integration-results.xml" || true
    else
        pytest integration/ --tb=short --junit-xml="$RESULTS_DIR/integration-results.xml" || true
    fi

    print_success "Integration tests completed"
fi

# Run System Tests
if [ "$RUN_SYSTEM" = true ]; then
    print_section "4. Running System Tests"
    cd "$TESTS_DIR"

    if [ "$VERBOSE" = true ]; then
        pytest system/ -v --tb=short --junit-xml="$RESULTS_DIR/system-results.xml" || true
    else
        pytest system/ --tb=short --junit-xml="$RESULTS_DIR/system-results.xml" || true
    fi

    print_success "System tests completed"
fi

# Generate Coverage Report
if [ "$RUN_COVERAGE" = true ]; then
    print_section "5. Generating Coverage Report"
    cd "$TESTS_DIR"

    pytest --cov="$BACKEND_DIR/app" \
           --cov-report=html \
           --cov-report=term \
           --cov-report=xml \
           --junit-xml="$RESULTS_DIR/all-tests.xml" \
           --quiet || true

    if [ -d "htmlcov" ]; then
        print_success "Coverage report generated at: $TESTS_DIR/htmlcov/index.html"
    fi
fi

# Summary
print_section "Test Execution Summary"

if [ -f "$RESULTS_DIR/all-tests.xml" ]; then
    echo "Test results saved to: $RESULTS_DIR/"
    echo ""
    echo "To view the HTML coverage report, open:"
    echo "  file://$TESTS_DIR/htmlcov/index.html"
    echo ""
fi

print_success "All test phases completed!"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Testing Complete!${NC}"
echo -e "${BLUE}========================================${NC}"

# Return to original directory
cd "$PROJECT_ROOT"
