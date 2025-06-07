from fastapi import APIRouter
from models import UserModel
from db import users_collection
from bson import ObjectId

router = APIRouter()

# Register a new user
@router.post("/users/register")
async def register_user(user_data: UserModel):
    user_dict = user_data.model_dump()
    user_dict["_id"] = str(ObjectId())
    await users_collection.insert_one(user_dict)
    return {"message": "User registered successfully", "user": user_dict}

# Get all registered users
@router.get("/users")
async def get_users():
    users = await users_collection.find().to_list(100)
    return {"users": users}
