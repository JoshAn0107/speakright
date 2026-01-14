#!/bin/bash

echo "===================================================================="
echo "Testing Registration Endpoint with curl"
echo "===================================================================="

BASE_URL="http://localhost:8000"
ENDPOINT="${BASE_URL}/api/auth/register"

echo ""
echo "Endpoint: ${ENDPOINT}"
echo ""

# Test 1: Register a student
echo "--------------------------------------------------------------------"
echo "Test 1: Register a new student"
echo "--------------------------------------------------------------------"

curl -X POST "${ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "curlstudent",
    "email": "curlstudent@example.com",
    "password": "CurlPass123!",
    "role": "student"
  }' \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s | python3 -m json.tool 2>/dev/null || echo "Response received"

echo ""
echo ""

# Test 2: Register a teacher
echo "--------------------------------------------------------------------"
echo "Test 2: Register a new teacher"
echo "--------------------------------------------------------------------"

curl -X POST "${ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "curlteacher",
    "email": "curlteacher@example.com",
    "password": "TeacherPass123!",
    "role": "teacher"
  }' \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s | python3 -m json.tool 2>/dev/null || echo "Response received"

echo ""
echo ""
echo "===================================================================="
echo "Tests completed!"
echo "===================================================================="
