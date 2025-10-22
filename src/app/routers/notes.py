from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field
import asyncio

router = APIRouter()

# ---------------- In-memory storage ----------------
_notes: list["Note"] = []
_next_id: int = 1
_lock = asyncio.Lock()


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field("", max_length=10_000)
    tags: list[str] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field("", max_length=10_000)
    tags: list[str] = Field(default_factory=list)


class Note(BaseModel):
    id: int
    title: str
    content: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime


def _find_index(note_id: int) -> int:
    for idx, n in enumerate(_notes):
        if n.id == note_id:
            return idx
    return -1


@router.post("", response_model=Note, status_code=201)
async def create_note(payload: NoteCreate) -> Note:
    global _next_id
    async with _lock:
        now = datetime.utcnow()
        note = Note(
            id=_next_id,
            title=payload.title,
            content=payload.content,
            tags=payload.tags,
            created_at=now,
            updated_at=now,
        )
        _notes.append(note)
        _next_id += 1
        return note


@router.get("", response_model=List[Note])
async def list_notes(
    q: Optional[str] = Query(default=None, description="Search in title or content"),
    tag: Optional[str] = Query(default=None, description="Filter by a single tag"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> list[Note]:
    data = _notes

    if q:
        q_lower = q.lower()
        data = [n for n in data if q_lower in n.title.lower() or q_lower in n.content.lower()]

    if tag:
        data = [n for n in data if tag in n.tags]

    # Simple pagination
    return data[offset : offset + limit]


@router.get("/{note_id}", response_model=Note)
async def get_note(note_id: int) -> Note:
    idx = _find_index(note_id)
    if idx < 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return _notes[idx]


@router.put("/{note_id}", response_model=Note)
async def update_note(note_id: int, payload: NoteUpdate) -> Note:
    idx = _find_index(note_id)
    if idx < 0:
        raise HTTPException(status_code=404, detail="Note not found")

    async with _lock:
        existing = _notes[idx]
        updated = existing.model_copy(
            update={
                "title": payload.title,
                "content": payload.content,
                "tags": payload.tags,
                "updated_at": datetime.utcnow(),
            }
        )
        _notes[idx] = updated
        return updated


@router.delete("/{note_id}", status_code=204, response_class=Response)
async def delete_note(note_id: int) -> Response:
    idx = _find_index(note_id)
    if idx < 0:
        raise HTTPException(status_code=404, detail="Note not found")

    async with _lock:
        _notes.pop(idx)
    return Response(status_code=204)
