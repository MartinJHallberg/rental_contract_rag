"""Contract validation services"""

from contract_loader import load_contract_and_extract_info
from rag import (
    validate_deposit_amount,
    validate_prepaid_rent,
    validate_termination_conditions,
    validate_price_adjustments,
)


def validate_contract_file(rag_chain, file_path):
    """Validate a contract file and return all validation results"""
    # Extract contract information
    contract_info = load_contract_and_extract_info(file_path)

    # Perform validations
    deposit_result = validate_deposit_amount(
        rag_chain, contract_info.deposit_amount, contract_info.monthly_rental_amount
    )

    prepaid_result = validate_prepaid_rent(
        rag_chain, contract_info.prepaid_rent, contract_info.monthly_rental_amount
    )

    termination_result = validate_termination_conditions(
        rag_chain, contract_info.termination_conditions
    )

    price_adjustment_result = validate_price_adjustments(
        rag_chain, contract_info.price_adjustments
    )

    return {
        "contract_info": contract_info,
        "deposit_result": deposit_result,
        "prepaid_result": prepaid_result,
        "termination_result": termination_result,
        "price_adjustment_result": price_adjustment_result,
    }
