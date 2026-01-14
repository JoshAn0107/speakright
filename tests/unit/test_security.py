"""
Unit tests for Security functions
Covers L01 Requirements: 3.d, 3.e, 3.f
"""
import pytest
import sys
from pathlib import Path
from jose import jwt
from datetime import datetime, timedelta

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token
)
from app.core.config import settings


class TestVerifyPassword:
    """
    L01 Requirement 3.d: The verify_password function should correctly
    validate passwords against stored hashes

    Testing approach: Functional category-partition testing
    Partitions: Correct password, incorrect password, case sensitivity,
                special characters
    """

    def test_correct_password_returns_true(self):
        """Test that correct password validates successfully"""
        password = "MySecurePassword123!"
        password_hash = get_password_hash(password)

        assert verify_password(password, password_hash) is True

    def test_incorrect_password_returns_false(self):
        """Test that incorrect password fails validation"""
        password = "MySecurePassword123!"
        wrong_password = "WrongPassword456!"
        password_hash = get_password_hash(password)

        assert verify_password(wrong_password, password_hash) is False

    def test_password_case_sensitivity(self):
        """Test that password validation is case-sensitive"""
        password = "MySecurePassword123!"
        password_hash = get_password_hash(password)

        # Different case should fail
        assert verify_password("mysecurepassword123!", password_hash) is False
        assert verify_password("MYSECUREPASSWORD123!", password_hash) is False

    def test_password_with_special_characters(self):
        """Test passwords with various special characters"""
        special_passwords = [
            "Pass!@#$%^&*()",
            "Test_Password-123",
            "My.Pass.Word+2024",
            "P@ssw0rd~`[]{}|"
        ]

        for password in special_passwords:
            password_hash = get_password_hash(password)
            assert verify_password(password, password_hash) is True
            assert verify_password(password + "x", password_hash) is False

    def test_empty_password(self):
        """Test handling of empty password"""
        password = "ValidPassword123"
        password_hash = get_password_hash(password)

        assert verify_password("", password_hash) is False

    def test_password_with_spaces(self):
        """Test password with leading/trailing/internal spaces"""
        password = "My Password 123"
        password_hash = get_password_hash(password)

        assert verify_password(password, password_hash) is True
        assert verify_password("My Password 123 ", password_hash) is False
        assert verify_password(" My Password 123", password_hash) is False

    def test_very_long_password(self):
        """Test validation of very long passwords"""
        password = "A" * 100 + "!@#$%^&*()" + "1234567890"
        password_hash = get_password_hash(password)

        assert verify_password(password, password_hash) is True
        assert verify_password(password[:-1], password_hash) is False

    def test_unicode_password(self):
        """Test password with unicode characters"""
        password = "Pässwörd123!你好"
        password_hash = get_password_hash(password)

        assert verify_password(password, password_hash) is True

    def test_password_with_only_numbers(self):
        """Test numeric-only password"""
        password = "123456789"
        password_hash = get_password_hash(password)

        assert verify_password(password, password_hash) is True
        assert verify_password("123456788", password_hash) is False


class TestGetPasswordHash:
    """
    L01 Requirement 3.e: The get_password_hash function should generate
    consistent hashes for the same password

    Testing approach: Black-box testing
    """

    def test_generates_valid_hash(self):
        """Test that function generates a valid hash"""
        password = "TestPassword123!"
        password_hash = get_password_hash(password)

        # Hash should not be empty
        assert password_hash is not None
        assert len(password_hash) > 0

        # Hash should be different from password
        assert password_hash != password

    def test_hash_can_be_verified(self):
        """Test that generated hash can be verified"""
        password = "TestPassword123!"
        password_hash = get_password_hash(password)

        # Should be able to verify the password
        assert verify_password(password, password_hash) is True

    def test_different_hashes_for_same_password(self):
        """Test that hashing same password twice produces different hashes (due to salt)"""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different (salted)
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_hash_consistency_verification(self):
        """Test that same password always verifies against its hash"""
        password = "TestPassword123!"
        password_hash = get_password_hash(password)

        # Verify multiple times
        for _ in range(10):
            assert verify_password(password, password_hash) is True

    def test_hash_format(self):
        """Test that hash has expected format (bcrypt)"""
        password = "TestPassword123!"
        password_hash = get_password_hash(password)

        # Bcrypt hashes start with $2b$
        assert password_hash.startswith("$2b$")

    def test_empty_password_hash(self):
        """Test hashing empty password"""
        password = ""
        password_hash = get_password_hash(password)

        assert password_hash is not None
        assert verify_password(password, password_hash) is True

    def test_long_password_hash(self):
        """Test hashing very long password"""
        password = "A" * 200
        password_hash = get_password_hash(password)

        assert password_hash is not None
        assert verify_password(password, password_hash) is True


class TestCreateAccessToken:
    """
    L01 Requirement 3.f: The create_access_token function should generate
    valid JWT tokens with correct claims

    Testing approach: Black-box testing
    """

    def test_creates_valid_jwt_token(self):
        """Test that function creates a valid JWT token"""
        user_id = "12345"
        token = create_access_token(data={"sub": user_id})

        # Token should not be empty
        assert token is not None
        assert len(token) > 0

        # Token should have three parts (header.payload.signature)
        assert token.count(".") == 2

    def test_token_contains_correct_user_id(self):
        """Test that token contains the correct user ID claim"""
        user_id = "12345"
        token = create_access_token(data={"sub": user_id})

        # Decode token (without verification for testing)
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert decoded["sub"] == user_id

    def test_token_contains_expiration(self):
        """Test that token includes expiration claim"""
        user_id = "12345"
        token = create_access_token(data={"sub": user_id})

        # Decode token
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Should have 'exp' claim
        assert "exp" in decoded
        assert isinstance(decoded["exp"], int)

        # Expiration should be in the future
        assert decoded["exp"] > datetime.utcnow().timestamp()

    def test_token_can_be_decoded(self):
        """Test that generated token can be decoded and validated"""
        user_id = "12345"
        token = create_access_token(data={"sub": user_id})

        # Should be able to decode with correct key and algorithm
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert decoded is not None
        assert "sub" in decoded

    def test_token_with_custom_expiration(self):
        """Test token creation with custom expiration time"""
        user_id = "12345"
        expires_delta = timedelta(hours=1)
        token = create_access_token(data={"sub": user_id}, expires_delta=expires_delta)

        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Calculate expected expiration
        expected_exp = datetime.utcnow() + expires_delta

        # Actual expiration should be close to expected (within 5 seconds)
        actual_exp = datetime.fromtimestamp(decoded["exp"])
        time_diff = abs((actual_exp - expected_exp).total_seconds())
        assert time_diff < 5

    def test_token_with_additional_claims(self):
        """Test token with additional custom claims"""
        token_data = {
            "sub": "12345",
            "role": "student",
            "email": "test@example.com"
        }
        token = create_access_token(data=token_data)

        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert decoded["sub"] == "12345"
        assert decoded.get("role") == "student"
        assert decoded.get("email") == "test@example.com"

    def test_token_signature_verification(self):
        """Test that token signature can be verified"""
        user_id = "12345"
        token = create_access_token(data={"sub": user_id})

        # Should decode successfully with correct key
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["sub"] == user_id

        # Should fail with wrong key
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, "wrong-secret-key", algorithms=[settings.ALGORITHM])

    def test_token_algorithm_verification(self):
        """Test that token uses correct algorithm"""
        user_id = "12345"
        token = create_access_token(data={"sub": user_id})

        # Should decode successfully with correct algorithm
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["sub"] == user_id

        # Should fail with wrong algorithm (if enforced)
        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS512"])
            # If it doesn't raise, the algorithm in header should still be HS256
            header = jwt.get_unverified_header(token)
            assert header["alg"] == settings.ALGORITHM
        except jwt.InvalidAlgorithmError:
            # Expected if algorithm validation is strict
            pass

    def test_different_users_get_different_tokens(self):
        """Test that different user IDs produce different tokens"""
        token1 = create_access_token(data={"sub": "12345"})
        token2 = create_access_token(data={"sub": "67890"})

        assert token1 != token2

        decoded1 = jwt.decode(token1, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        decoded2 = jwt.decode(token2, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert decoded1["sub"] == "12345"
        assert decoded2["sub"] == "67890"

    def test_token_header_structure(self):
        """Test that token header has expected structure"""
        user_id = "12345"
        token = create_access_token(data={"sub": user_id})

        # Get header without verification
        header = jwt.get_unverified_header(token)

        # Should specify algorithm
        assert "alg" in header
        assert header["alg"] == settings.ALGORITHM

        # Should specify token type
        assert "typ" in header
        assert header["typ"] == "JWT"

    def test_token_expiration_default(self):
        """Test that default expiration is set correctly"""
        user_id = "12345"
        token = create_access_token(data={"sub": user_id})

        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Calculate expected expiration based on settings
        expected_exp = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        # Actual expiration should be close to expected
        actual_exp = datetime.fromtimestamp(decoded["exp"])
        time_diff = abs((actual_exp - expected_exp).total_seconds())
        assert time_diff < 5  # Within 5 seconds

    def test_expired_token_detection(self):
        """Test that expired tokens can be detected"""
        user_id = "12345"
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data={"sub": user_id}, expires_delta=expires_delta)

        # Should raise ExpiredSignatureError
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
