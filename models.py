from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field


class TranslationModel(BaseModel):
    translator_auth_id: str
    language: str
    english_sentence: str
    translated_sentence: str
    source: str = Field(..., pattern="^(original|sentence_db|flagged)$")
    timestamp: datetime = datetime.now(timezone.utc)


class SentenceModel(BaseModel):
    english_sentence: str
    language_translated: list[str] = []
    timestamp: datetime = datetime.now(timezone.utc)

class UserModel(BaseModel):
    firebaseuid: str
    name: str
    role: str = "user"  # "user" or "admin"
    timestamp: datetime = datetime.now(timezone.utc)

class TranslationResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str

class TranslationRequest(BaseModel):
    text: str