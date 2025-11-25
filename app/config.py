"""Application configuration using environment variables."""

import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Simple settings class that reads from environment variables."""
    
    # Redis
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    
    # Pinecone
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "fastapi-rag-ec2")
    
    # Langfuse (optional - for tracing)
    langfuse_public_key: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    langfuse_secret_key: str = os.getenv("LANGFUSE_SECRET_KEY", "")
    langfuse_host: str = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    # Google AI
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")


@lru_cache
def get_settings() -> Settings:
    return Settings()

