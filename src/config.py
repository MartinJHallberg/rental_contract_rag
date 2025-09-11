import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# LangSmith Configuration
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")
if not LANGCHAIN_PROJECT:
    raise ValueError("LANGCHAIN_PROJECT environment variable is required")
ENABLE_TRACING = os.getenv("ENABLE_TRACING", "true").lower() == "true"

# OpenAI Configuration  
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# RAG Configuration
VECTOR_STORE_DIR = Path("src/data/vector_stores")
EMBEDDING_MODEL = "text-embedding-3-small"
COLLECTION_NAME = "rental_law_2025"
CACHE_DIR = Path("src/data/cache")
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.0

# Setup LangSmith tracing
if LANGCHAIN_API_KEY and ENABLE_TRACING:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
    print(f"✅ LangSmith tracing enabled for: {LANGCHAIN_PROJECT}")
elif ENABLE_TRACING:
    print("⚠️ LangSmith tracing requested but LANGCHAIN_API_KEY not found")