from __future__ import annotations

import asyncio
import hashlib
from datetime import datetime, UTC
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query, Response
from pydantic import BaseModel, Field

router = APIRouter()

# ---------------- In-memory storage ----------------
_notes: list["Note"] = []
_next_id: int = 1
_lock = asyncio.Lock()


# ---------------- Models ----------------
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


class NotesPage(BaseModel):
    items: list[Note]
    total: int
    limit: int
    offset: int


# ---------------- Helpers ----------------
def _find_index(note_id: int) -> int:
    for idx, n in enumerate(_notes):
        if n.id == note_id:
            return idx
    return -1


def _note_etag(note: Note) -> str:
    h = hashlib.sha256(
        f"{note.id}:{note.title}:{note.content}:{note.updated_at.isoformat()}".encode()
    ).hexdigest()
    return f'W/"{h}"'  # weak ETag is fine here


# ---------------- Routes ----------------
@router.post("", response_model=Note, status_code=201)
async def create_note(payload: NoteCreate) -> Note:
    global _next_id
    async with _lock:
        now = datetime.now(UTC)
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


@router.get("", response_model=NotesPage)
async def list_notes(
    q: Optional[str] = Query(default=None, description="Search in title or content"),
    tag: Optional[str] = Query(default=None, description="Filter by a single tag"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> NotesPage:
    """List notes with optional search, tag filter, and pagination."""
    data = _notes

    if q:
        q_lower = q.lower()
        data = [n for n in data if q_lower in n.title.lower() or q_lower in n.content.lower()]

    if tag:
        data = [n for n in data if tag in n.tags]

    total = len(data)
    items = data[offset : offset + limit]

    return NotesPage(items=items, total=total, limit=limit, offset=offset)


@router.get("/{note_id}")
async def get_note(note_id: int, if_none_match: str | None = Header(default=None)) -> Response:
    idx = _find_index(note_id)
    if idx < 0:
        raise HTTPException(status_code=404, detail="Note not found")
    note = _notes[idx]
    etag = _note_etag(note)
    if if_none_match == etag:
        return Response(status_code=304, headers={"ETag": etag})
    return Response(
        content=note.model_dump_json(),
        media_type="application/json",
        headers={"ETag": etag},
    )


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
                "updated_at": datetime.now(UTC),
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
