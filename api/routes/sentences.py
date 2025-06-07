from fastapi import APIRouter
from models import SentenceModel
from db import pending_translations_collection
from bson import ObjectId

router = APIRouter()

# Retrieve one untranslated sentence
@router.get("/sentences/next")
async def get_next_sentence(language: str):
    sentence = await pending_translations_collection.find_one(
        {"language_translated": {"$nin": [language]}}  # Ensures sentence hasn't been translated into this language
    )
    if sentence:
        return {"sentence": sentence}
    return {"message": "No sentences available for translation"}

# Add a new English sentence
@router.post("/sentences")
async def add_sentence(sentence_data: SentenceModel):
    sentence_dict = sentence_data.model_dump()
    sentence_dict["_id"] = str(ObjectId())
    await pending_translations_collection.insert_one(sentence_dict)
    return {"message": "Sentence added successfully", "sentence": sentence_dict}

# Update sentence after translation
@router.put("/sentences/{sentence_id}")
async def update_sentence(sentence_id: str, language: str):
    update_result = await pending_translations_collection.update_one(
        {"_id": sentence_id},
        {"$push": {"language_translated": language}}  # Only appends the new language to prevent duplicate translations
    )
    if update_result.modified_count:
        return {"message": "Sentence updated successfully"}
    return {"error": "Sentence not found"}
