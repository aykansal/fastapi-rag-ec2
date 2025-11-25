"""RAG service - handles document loading, embedding, and retrieval."""

import bs4
from redis import Redis
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_redis import RedisSemanticCache
from langchain_core.globals import set_llm_cache
from langgraph.graph import StateGraph, END

from langfuse import get_client
from langfuse.langchain import CallbackHandler

from app.config import get_settings

settings = get_settings()

# ─────────────────────────────────────────────────────────────
# Langfuse setup
# ─────────────────────────────────────────────────────────────
langfuse = get_client()

if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

langfuse_handler = CallbackHandler()

# ─────────────────────────────────────────────────────────────
# Clients & Embeddings
# ─────────────────────────────────────────────────────────────

def get_redis_client() -> Redis:
    """Create Redis client for semantic caching."""
    return Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True,
        username="default",
        password=settings.redis_password,
    )


def get_embedder() -> GoogleGenerativeAIEmbeddings:
    """Create Google AI embeddings model."""
    return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")


def get_llm() -> ChatGoogleGenerativeAI:
    """Create Google AI chat model."""
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash")


def get_pinecone_index():
    """Get or create Pinecone index."""
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index_name = settings.pinecone_index_name
    
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    
    return pc.Index(index_name)


# ─────────────────────────────────────────────────────────────
# Document Ingestion
# ─────────────────────────────────────────────────────────────

def ingest_from_url(url: str) -> int:
    """Load a webpage, chunk it, embed, and store in Pinecone."""
    # Load and parse HTML
    bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
    loader = WebBaseLoader(web_paths=(url,), bs_kwargs={"parse_only": bs4_strainer})
    docs = loader.load()
    
    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    
    # Embed and upsert to Pinecone
    embedder = get_embedder()
    index = get_pinecone_index()
    
    vectors = []
    for i, chunk in enumerate(chunks):
        vectors.append({
            "id": f"doc-{i}",
            "values": embedder.embed_query(chunk.page_content),
            "metadata": {"text": chunk.page_content, "source": url},
        })
    
    index.upsert(vectors)
    return len(chunks)


# ─────────────────────────────────────────────────────────────
# RAG Graph
# ─────────────────────────────────────────────────────────────

def build_rag_graph():
    """Build the RAG pipeline using LangGraph."""
    embedder = get_embedder()
    index = get_pinecone_index()
    llm = get_llm()
    
    def retrieve(state: dict) -> dict:
        """Retrieve relevant context from Pinecone."""
        query = state["input"]
        q_emb = embedder.embed_query(query)
        results = index.query(vector=q_emb, top_k=3, include_metadata=True)
        context = "\n".join([m.metadata["text"] for m in results.matches])
        state["context"] = context
        return state
    
    def generate(state: dict) -> dict:
        """Generate answer using LLM with retrieved context."""
        prompt = f"Use the context below to answer.\nContext:\n{state['context']}\nUser: {state['input']}"
        response = llm.invoke(prompt)
        state["output"] = response.content
        return state
    
    # Build graph
    graph = StateGraph(dict)
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    
    return graph.compile()


# ─────────────────────────────────────────────────────────────
# Cache Setup (optional)
# ─────────────────────────────────────────────────────────────

def setup_semantic_cache():
    """Enable Redis semantic caching for LLM responses."""
    try:
        redis_client = get_redis_client()
        embedder = get_embedder()
        set_llm_cache(RedisSemanticCache(redis_client=redis_client, embeddings=embedder))
        return True
    except Exception:
        return False


# Lazy-loaded RAG graph
_rag_graph = None

def get_rag_graph():
    """Get or create the RAG graph (singleton)."""
    global _rag_graph
    if _rag_graph is None:
        _rag_graph = build_rag_graph()
    return _rag_graph


def query(question: str) -> str:
    """Run a query through the RAG pipeline."""
    rag = get_rag_graph()
    result = rag.invoke({"input": question}, config={"callbacks": [langfuse_handler]})
    return result["output"]

