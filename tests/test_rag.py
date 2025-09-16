import pytest
from unittest.mock import Mock
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from rag import RAGChain, validate_deposit_amount, LLMOutput
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


@pytest.fixture
def rag_chain():
    return RAGChain()


@pytest.mark.api_call
def test_rag_chain(rag_chain):
    deposit_answer = validate_deposit_amount(
        rag_chain, deposit_amount="50000 DKK", monthly_rental_amount="4000 DKK"
    )
    assert isinstance(deposit_answer, LLMOutput)
    assert deposit_answer.should_be_checked is True


@pytest.mark.slow
@pytest.mark.api_call
def test_load_and_extract_contract_info_correct(rag_chain):
    file_path = "src/data/contract_everything_correct.pdf"
    extracted_contract_info = load_contract_and_extract_info(file_path)

    deposit_answer = validate_deposit_amount(
        rag_chain,
        deposit_amount=extracted_contract_info.deposit_amount,
        monthly_rental_amount=extracted_contract_info.monthly_rental_amount,
    )

    assert deposit_answer.should_be_checked is False


@pytest.mark.slow
@pytest.mark.api_call
def test_load_and_extract_contract_info_deposit_incorrect(rag_chain):
    file_path = "src/data/contract_incorrect_deposit.pdf"
    extracted_contract_info = load_contract_and_extract_info(file_path)

    deposit_answer = validate_deposit_amount(
        rag_chain,
        deposit_amount=extracted_contract_info.deposit_amount,
        monthly_rental_amount=extracted_contract_info.monthly_rental_amount,
    )

    assert deposit_answer.should_be_checked is True
