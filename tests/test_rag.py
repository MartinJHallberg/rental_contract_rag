import pytest
from unittest.mock import Mock, patch
from langchain.schema import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from rag import SimpleRAGChain


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


def test_rag_chain_with_real_retriever(sample_documents, mock_embeddings):
    """Test RAGChain with real vector store and retriever, but mock LLM"""

    # Create real vector store with mock embeddings
    vector_store = InMemoryVectorStore.from_documents(
        documents=sample_documents, embedding=mock_embeddings
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": 2})

    # Create real prompt
    prompt = ChatPromptTemplate.from_template(
        "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    )

    # Mock LLM to avoid API calls
    mock_llm = Mock(spec=ChatOpenAI)
    mock_llm.invoke.return_value = Mock(content="Mocked LLM response")

    # Create RAG chain
    rag = SimpleRAGChain(retriever=retriever, llm=mock_llm, prompt=prompt)

    # Test that retriever works
    retrieved_docs = retriever.invoke("deposit")
    assert len(retrieved_docs) <= 2
    assert all(isinstance(doc, Document) for doc in retrieved_docs)

    # Test format_docs with real documents
    formatted = rag._format_docs(sample_documents)
    expected = (
        "§ 1. This law applies to rental agreements for residential properties.\n\n"
        "§ 2. The landlord must provide written notice before entering the property.\n\n"
        "§ 50. Maximum deposit is 3 months rent for residential properties."
    )
    assert formatted == expected
