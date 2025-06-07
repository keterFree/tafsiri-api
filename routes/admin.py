from fastapi import APIRouter, HTTPException
from db import translations_collection, users_collection
from bson import ObjectId
from datetime import datetime

router = APIRouter()

async def get_admin_user(user_uid: str):
    return await users_collection.find_one({"firebaseuid": user_uid, "role": "admin"})

@router.get("/admin/unverified")
async def get_unverified_translations(
    skip: int = 0, 
    limit: int = 20, 
    translator_auth_id: str = None, 
    language: str = None, 
    source: str = None, 
    timestamp_start: datetime = None, 
    timestamp_end: datetime = None
):
    query = {"verified": False}

    if translator_auth_id:
        query["translator_auth_id"] = translator_auth_id

    if language:
        query["language"] = language

    if source:
        query["source"] = source

    if timestamp_start and timestamp_end:
        query["timestamp"] = {"$gte": timestamp_start, "$lte": timestamp_end}

    translations = await translations_collection.find(query).skip(skip).limit(limit).to_list(100)
    return {"translations": translations}

@router.put("/admin/verify/{translation_id}")
async def verify_translation(translation_id: str, verifier_uid: str):
    admin_user = await get_admin_user(verifier_uid)
    if not admin_user:
        raise HTTPException(status_code=403, detail="Unauthorized: Admin access required")

    update_result = await translations_collection.update_one(
        {"_id": ObjectId(translation_id)},
        {"$set": {"verified": True, "verified_by": verifier_uid}}
    )
    return {"message": "Translation verified"} if update_result.modified_count else {"error": "Translation not found"}

@router.put("/admin/reject/{translation_id}")
async def reject_translation(translation_id: str, verifier_uid: str):
    admin_user = await get_admin_user(verifier_uid)
    if not admin_user:
        raise HTTPException(status_code=403, detail="Unauthorized: Admin access required")

    update_result = await translations_collection.update_one(
        {"_id": ObjectId(translation_id)},
        {"$set": {"status": "rejected", "rejected_by": verifier_uid}}
    )
    return {"message": "Translation rejected"} if update_result.modified_count else {"error": "Translation not found"}
