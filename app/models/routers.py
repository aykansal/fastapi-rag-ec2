from pydantic import BaseModel, HttpUrl

class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str


class IngestRequest(BaseModel):
    url: HttpUrl


class IngestResponse(BaseModel):
    message: str
    chunks_created: int
