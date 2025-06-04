from fastapi import APIRouter
from models import TranslationModel
from db import translations_collection
from bson import ObjectId

router = APIRouter()

# Add a translation
@router.post("/contributions")
async def add_translation(translation_data: TranslationModel):
    translation_dict = translation_data.model_dump()
    translation_dict["_id"] = str(ObjectId())  # Unique MongoDB ID
    await translations_collection.insert_one(translation_dict)
    return {"message": "Translation added successfully", "translation": translation_dict}

# Get all translations
@router.get("/contributions")
async def get_all_translations(skip: int = 0, limit: int = 20, source: str = None, language: str = None):
    query = {}  # Initialize an empty query
    
    if source:
        query["source"] = source  # Filter by translation source
    
    if language:
        query["language"] = language  # Filter by target language
    
    translations = await translations_collection.find(query).skip(skip).limit(limit).to_list(100)
    return {"translations": translations}



# Search translations with regex
@router.get("/contributions/search")
async def search_translation(language: str = None, english_sentence: str = None):
    query = {}
    if language:
        query["language"] = language
    if english_sentence:
        query["english_sentence"] = {"$regex": f"^{english_sentence}$", "$options": "i"}  # Case-insensitive match

    translations = await translations_collection.find(query).to_list(100)
    return {"translations": translations}
