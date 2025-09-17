import pytest
from contract_loader import (
    parse_contract_pdf_to_text,
    load_contract_and_extract_info,
    ContractInfo,
)


@pytest.mark.slow
def test_parse_contract_pdf_to_text():
    file_path = "src/data/contract_everything_correct.pdf"
    rental_contract = parse_contract_pdf_to_text(file_path)
    assert "Typeformular" in rental_contract.text


@pytest.mark.slow
@pytest.mark.api_call
def test_load_and_extract_contract_info():
    file_path = "src/data/contract_everything_correct.pdf"
    extracted_contract_info = load_contract_and_extract_info(file_path)

    assert isinstance(extracted_contract_info, ContractInfo)
    assert extracted_contract_info.prepaid_rent == "9000 kr"
    assert extracted_contract_info.landlord == "Martin Hallberg"
    assert extracted_contract_info.tenant == "Martin Hallberg"
    assert extracted_contract_info.monthly_rental_amount == "3000 kr"
    assert extracted_contract_info.deposit_amount == "9000 kr"
