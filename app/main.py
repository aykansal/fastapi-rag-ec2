"""FastAPI application entrypoint."""

from fastapi import APIRouter, FastAPI

from app.routers.rag import router as rag_router

app = FastAPI(
    title="RAG API",
    description="Simple RAG API with Pinecone and Google AI",
    version="1.0.0",
)

app.include_router(rag_router, prefix="/api/v1", tags=["api"])


@app.get("/")
def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "message": "RAG API is running"}
