from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers.notes import router as notes_router
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Memo Notes API",
    version="0.1.0",
    docs_url="/",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET","POST","PUT","DELETE","PATCH","OPTIONS"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def unhandled_exc_handler(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": str(exc)}},
    )

@app.get("/healthz", status_code=status.HTTP_200_OK, tags=["infra"])
async def healthz():
    return {"status": "ok"}

app.include_router(notes_router, prefix="/v1/notes", tags=["notes"])
