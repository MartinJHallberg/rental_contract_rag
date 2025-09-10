import pytest
from contract_loader import parse_contract_pdf_to_text, load_contract_and_extract_info


@pytest.mark.slow
def test_parse_contract_pdf_to_text():
    file_path = "src/data/contract_template_with_info_printed.pdf"
    text = parse_contract_pdf_to_text(file_path)
    assert "Typeformular" in text


@pytest.mark.slow
@pytest.mark.api_call
def test_load_and_extract_contract_info():
    file_path = "src/data/contract_template_with_info_printed.pdf"
    contract_info = load_contract_and_extract_info(file_path)
    assert isinstance(contract_info, dict)
    assert "landlord" in contract_info
    assert "tenant" in contract_info
    assert "monthly_rental_amount" in contract_info
    assert "payment_terms" in contract_info
    assert "rental_type" in contract_info
    assert "property_address" in contract_info
    assert "lease_start_date" in contract_info
    assert "lease_duration" in contract_info
    assert "termination_conditions" in contract_info
    assert "price_adjustments" in contract_info
    assert "deposit_amount" in contract_info
    assert "prepaid_rent" in contract_info
    assert "amenities" in contract_info
    assert "utilities" in contract_info
    assert "renters_responsibilities" in contract_info
