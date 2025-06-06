from datetime import datetime, timedelta, timezone  # Added imports here
from models import TranslationModel
from bson import ObjectId
from fastapi import APIRouter, Query
from db import translations_collection
from typing import Optional

# import logging

# Configure logging
# logging.basicConfig(level=logging.DEBUG)
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
async def get_all_translations(
    skip: int = 0,
    limit: int = 20,
    source: str = None,
    language: str = None,
    translator_auth_id: str = None  # New filter parameter
):
    query = {}
    
    if source:
        query["source"] = source
    if language:
        query["language"] = language
    if translator_auth_id:  # New filter condition
        query["translator_auth_id"] = translator_auth_id
    
    translations = await translations_collection.find(query).skip(skip).limit(limit).to_list(100)
    return {"translations": translations}


@router.get("/contributions/stats")
async def get_contribution_stats(translator_auth_id: str, time_filter: str = "all"):
    today = datetime.now(timezone.utc)
    date_filter = {}

    if time_filter == "week":
        start_date = today - timedelta(days=7)
        date_filter = {"timestamp": {"$gte": start_date}}
    elif time_filter == "month":
        start_date = today - timedelta(days=30)
        date_filter = {"timestamp": {"$gte": start_date}}

    query = {"translator_auth_id": translator_auth_id}
    query.update(date_filter)

    # DEBUG: Print query
    #logging.debug(f"Query for stats: {query}")

    total_count = await translations_collection.count_documents(query)
    #logging.debug(f"Total translations: {total_count}")

    source_pipeline = [
        {"$match": {"translator_auth_id": translator_auth_id, **date_filter}},
        {"$group": {"_id": "$source", "count": {"$sum": 1}}}
    ]
    by_source = await translations_collection.aggregate(source_pipeline).to_list(None)
    #logging.debug(f"By source: {by_source}")
    by_source = {item["_id"]: item["count"] for item in by_source}

    language_pipeline = [
        {"$match": {"translator_auth_id": translator_auth_id, **date_filter}},
        {"$group": {"_id": "$language", "count": {"$sum": 1}}}
    ]
    by_language = await translations_collection.aggregate(language_pipeline).to_list(None)
    #logging.debug(f"By language: {by_language}")
    by_language = {item["_id"]: item["count"] for item in by_language}

    daily_pipeline = [
        {"$match": {"translator_auth_id": translator_auth_id, **date_filter}},
        {"$project": {
            "date": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": "$timestamp"
                }
            }
        }},
        {"$group": {
            "_id": "$date",
            "count": {"$sum": 1},
            "dateObj": {"$first": {"$dateFromString": {"dateString": "$date"}}}
        }},
        {"$sort": {"dateObj": 1}},
        {"$project": {
            "_id": 1,
            "count": 1,
            "date": "$_id"
        }}
    ]
    daily_contributions = await translations_collection.aggregate(daily_pipeline).to_list(None)
    #logging.debug(f"Daily contributions: {daily_contributions}")

    last_contribution = await translations_collection.find_one(
        {"translator_auth_id": translator_auth_id, **date_filter},
        sort=[("timestamp", -1)]
    )
    #logging.debug(f"Last contribution: {last_contribution}")

    return {
        "total": total_count,
        "by_source": by_source,
        "by_language": by_language,
        "daily_contributions": daily_contributions,
        "languages_count": len(by_language),
        "last_contribution": last_contribution
    }

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