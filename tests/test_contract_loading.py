import pytest
from contract_loader import (
    parse_contract_pdf_to_text,
    load_contract_and_extract_info,
    ContractInfo,
)


@pytest.mark.slow
def test_parse_contract_pdf_to_text():
    file_path = "src/data/contract_template_with_info_printed.pdf"
    text = parse_contract_pdf_to_text(file_path)
    assert "Typeformular" in text


@pytest.mark.slow
@pytest.mark.api_call
def test_load_and_extract_contract_info():
    file_path = "src/data/contract_template_with_info_printed.pdf"
    extracted_contract_info = load_contract_and_extract_info(file_path)
    assert isinstance(extracted_contract_info, ContractInfo)
