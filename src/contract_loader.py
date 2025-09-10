from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain import LLMChain
from langchain_community.chat_models import ChatOpenAI
from pdf2image import convert_from_path
import pytesseract


def parse_contract_pdf_to_text(file_path: str) -> str:
    pages = convert_from_path(
        file_path,
        poppler_path=r"C:\Projects\poppler-25.07.0\Library\bin",
    )
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page)

    return text


def extract_contract_info(contract_text: str):
    """Extract key information from a rental contract using an LLM"""

    prompt_contract_all_info = """
    You are a helpful assistant that summarizes rental contracts.
    Extract the main information from the rental contract below. Focus on key details such as:
    - Parties involved (landlord and tenant)
    - Monthly rental amount and payment terms
    - Rental type (lejemål), ownership, andel, rental, subrental, room or other
    - Address
    - Start date of the lease
    - Duration of the lease and termination conditions
    - Deposit amount and prepaid rent
    - How and when rent can be adjusted
    - What amenities are included (e.g., parking, dishwasher, etc.)
    - What utilities are included (e.g., heating, water, electricity, internet, etc.)
    - Renters responsibilities and obligations, specifically regarding inside and outside maintenance, repairs, and what they include,and any other duties outlined in the contract.

    

    Answer with in a json format with keys, as specified in example below. Do not add or change any key in the json.
    "landlord": "John Doe",
    "tenant": "Maria Smith",
    "monthly_rental_amount": "3000 DKK",
    "payment_terms": "First of each month",
    "rental_type": "Ejerlejlighed",
    "property_address": "Street 123, City, ZIP",
    "lease_start_date": "2023-01-01",
    "lease_duration": "12 months",
    "termination_conditions": "3 months notice",
    "price_adjustments": "Rent can be adjusted annually based on CPI",
    "deposit_amount": "6000 DKK",
    "prepaid_rent": "3000 DKK",
    "amenities": "Parking, Dishwasher",
    "utilities": "heating": "Included", "water": "Included", "electricity": "Included", "internet": "Included",
    "renters_responsibilities": 
        "inside_maintenance": "Tenant is responsible for all inside maintenance",
            "outside_maintenance": "Landlord is responsible for outside maintenance",
        "repairs": "Tenant must report all repairs needed"

    Always include all the above keys, even if it is not explicitly stated in the contract.

    {contract_text}
    """
    llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0)

    # Define the expected schema for the output
    response_schemas = [
        ResponseSchema(name="landlord", description="Name of the landlord"),
        ResponseSchema(name="tenant", description="Name of the tenant"),
        ResponseSchema(
            name="monthly_rental_amount", description="Monthly rental amount"
        ),
        ResponseSchema(name="payment_terms", description="Payment terms"),
        ResponseSchema(
            name="rental_type",
            description="Type of property, ownership, rental, andel, single room, sublent or other",
        ),
        ResponseSchema(name="property_address", description="Property address"),
        ResponseSchema(name="lease_start_date", description="Lease start date"),
        ResponseSchema(name="lease_duration", description="Duration of the lease"),
        ResponseSchema(
            name="termination_conditions", description="Termination conditions"
        ),
        ResponseSchema(
            name="price_adjustments", description="Price adjustment conditions"
        ),
        ResponseSchema(name="deposit_amount", description="Deposit amount"),
        ResponseSchema(name="prepaid_rent", description="Prepaid rent"),
        ResponseSchema(name="amenities", description="Amenities included"),
        ResponseSchema(
            name="utilities",
            description="Utilities included, and if they are included or not",
        ),
        ResponseSchema(
            name="renters_responsibilities",
            description="Responsibilities of the renter, specifically regarding inside and outside maintenance, repairs, and any other duties outlined in the contract",
        ),
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

    prompt_template = PromptTemplate(
        template=prompt_contract_all_info,
        input_variables=["contract_text"],
        output_parser=output_parser,
    )

    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt_template,
        output_parser=output_parser,
    )

    result = llm_chain.run(contract_text=contract_text)

    return result


def load_contract_and_extract_info(file_path: str):
    contract_text = parse_contract_pdf_to_text(file_path)
    contract_info = extract_contract_info(contract_text)
    return contract_info
