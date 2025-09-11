import pytest
from unittest.mock import Mock, patch
from langchain.schema import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from rag import RAGChain, validate_deposit_amount
from contract_loader import load_contract_and_extract_info


@pytest.fixture
def sample_documents():
    """Create sample rental law documents"""
    return [
        Document(
            page_content="§ 1. This law applies to rental agreements for residential properties.",
            metadata={"chapter": "Chapter 1", "paragraph": 1, "page": 1},
        ),
        Document(
            page_content="§ 2. The landlord must provide written notice before entering the property.",
            metadata={"chapter": "Chapter 1", "paragraph": 2, "page": 1},
        ),
        Document(
            page_content="§ 50. Maximum deposit is 3 months rent for residential properties.",
            metadata={"chapter": "Chapter 5", "paragraph": 50, "page": 15},
        ),
    ]


@pytest.fixture
def mock_embeddings():
    """Mock embeddings to avoid API calls"""
    mock_embeddings = Mock(spec=OpenAIEmbeddings)
    # Return dummy embeddings (same dimension for all texts)
    mock_embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]] * 10
    mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
    return mock_embeddings



def test_rag_chain():
    rag_chain = RAGChain()

    extracted_contract_info = load_contract_and_extract_info("src/data/contract_template_with_info_printed.pdf")

    deposit_answer = validate_deposit_amount(rag_chain, extracted_contract_info)