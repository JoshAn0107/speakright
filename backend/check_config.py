from app.core.config import settings

print(f"SECRET_KEY: {settings.SECRET_KEY}")
print(f"ALGORITHM: {settings.ALGORITHM}")
print(f"DATABASE_URL: {settings.DATABASE_URL}")
print(f"AZURE_SPEECH_KEY: {settings.AZURE_SPEECH_KEY[:20] if settings.AZURE_SPEECH_KEY else 'None'}...")
