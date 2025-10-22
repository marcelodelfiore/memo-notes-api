from fastapi import FastAPI
from app.routers.notes import router as notes_router

app = FastAPI(title="Memo Notes API", version="0.1.0")

app.include_router(notes_router, prefix="/notes", tags=["notes"])
