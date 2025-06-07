from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from db import client
from routes import sentences,contributions, users, admin
from routes.models.kalenjin import routes

app = FastAPI()
app.include_router(contributions.router)
app.include_router(sentences.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://tafsiri-frontend-phi.vercel.app",
        "https://www.tafsiri.site",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Welcome to the Translation API"}

@app.get("/health")
async def health():
    try:
        # Correct way to ping MongoDB
        await client.admin.command("ping")
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "database down", "error": str(e)}