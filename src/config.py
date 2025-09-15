import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()
CACHE_DIR = Path("src/data/cache")

# LangSmith Configuration - defaults for CI/testing
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "rental-contract-rag")
ENABLE_TRACING = os.getenv("ENABLE_TRACING", "true").lower() == "true"

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# RAG Configuration
VECTOR_STORE_DIR = Path("src/data/vector_stores")
EMBEDDING_MODEL = "text-embedding-3-small"
COLLECTION_NAME = "rental_law_2025"

# LLM Configuration
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.0

# Setup LangSmith tracing - only if explicitly enabled AND API key available
if ENABLE_TRACING and LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
    print(f"✅ LangSmith tracing enabled for: {LANGCHAIN_PROJECT}")
else:
    # Explicitly disable tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    if "LANGCHAIN_API_KEY" in os.environ:
        del os.environ["LANGCHAIN_API_KEY"]  # Remove to prevent accidental tracing
    print("🔇 LangSmith tracing disabled")
