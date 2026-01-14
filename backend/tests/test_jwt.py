from jose import jwt, JWTError
from app.core.config import settings
from app.core.security import create_access_token, decode_access_token

# Create a token
token = create_access_token(data={"sub": 1})
print(f"Generated token: {token[:50]}...")

# Try to decode it
try:
    payload = decode_access_token(token)
    print(f"Decoded payload: {payload}")
except Exception as e:
    print(f"Error decoding: {e}")

# Also try manually
try:
    manual_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print(f"Manual decode: {manual_payload}")
except JWTError as e:
    print(f"JWT Error: {e}")
