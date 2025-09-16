"""Sample contracts configuration"""

SAMPLE_CONTRACTS = [
    {
        "id": "contract_everything_correct",
        "title": "✅ Compliant Contract",
        "description": "A rental contract that follows all Danish rental law requirements.",
        "filename": "contract_everything_correct.pdf",
        "color": "primary"
    },
    {
        "id": "contract_incorrect_deposit",
        "title": "⚠️ Incorrect Deposit",
        "description": "A contract with deposit amount issues that violate Danish rental law.",
        "filename": "contract_incorrect_deposit.pdf",
        "color": "primary"
    },
    {
        "id": "contract_incorrect_prepaid_rent",
        "title": "⚠️ Incorrect Prepaid Rent",
        "description": "A contract with prepaid rent issues that violate Danish rental law.",
        "filename": "contract_incorrect_prepaid_rent.pdf",
        "color": "primary"
    }
]
