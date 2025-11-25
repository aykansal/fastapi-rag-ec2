"""RAG router providing ingestion, query, and cache endpoints."""

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.lib import rag as rag_service
from app.models.routers import QueryRequest, QueryResponse, IngestRequest, IngestResponse

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/query", response_model=QueryResponse)
def ask_question(request: QueryRequest) -> QueryResponse:
    """Ask a question through the RAG pipeline."""
    try:
        answer = rag_service.query(request.question)
        return QueryResponse(answer=answer)
    except Exception as exc:  # pragma: no cover - surface runtime issues
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/ingest", response_model=IngestResponse)
def ingest_document(request: IngestRequest) -> IngestResponse:
    """Ingest a document from a URL."""
    try:
        chunks = rag_service.ingest_from_url(str(request.url))
        return IngestResponse(
            message=f"Successfully ingested {request.url}",
            chunks_created=chunks,
        )
    except Exception as exc:  # pragma: no cover - surface runtime issues
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/cache/enable")
def enable_cache() -> dict[str, str]:
    """Enable Redis semantic caching."""
    success = rag_service.setup_semantic_cache()
    if success:
        return {"message": "Semantic cache enabled"}
    return {"message": "Failed to enable cache - check Redis connection"}

