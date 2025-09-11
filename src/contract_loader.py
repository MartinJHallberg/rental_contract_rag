from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain import LLMChain
from langchain_community.chat_models import ChatOpenAI
from pdf2image import convert_from_path
import pytesseract


from pydantic import BaseModel, Field
from typing import Dict, Optional
from langchain.output_parsers import PydanticOutputParser


class ContractInfo(BaseModel):
    """Pydantic model for rental contract information"""

    landlord: str = Field(description="Parties involved (landlord and tenant)")
    tenant: str = Field(description="Parties involved (landlord and tenant)")
    monthly_rental_amount: str = Field(
        description="Monthly rental amount and payment terms"
    )
    payment_terms: str = Field(description="Monthly rental amount and payment terms")
    rental_type: str = Field(
        description="Rental type (lejemål), ownership, andel, rental, subrental, room or other"
    )
    property_address: str = Field(description="Address")
    lease_start_date: str = Field(description="Start date of the lease")
    lease_duration: str = Field(
        description="Duration of the lease and termination conditions"
    )
    termination_conditions: str = Field(
        description="Duration of the lease and termination conditions"
    )
    price_adjustments: str = Field(description="How and when rent can be adjusted")
    deposit_amount: str = Field(description="Deposit amount and prepaid rent")
    prepaid_rent: str = Field(description="Deposit amount and prepaid rent")
    amenities: str = Field(
        description="What amenities are included (e.g., parking, dishwasher, etc.)"
    )
    utilities: Dict[str, str] = Field(
        description="What utilities are included (e.g., heating, water, electricity, internet, etc.)",
        default_factory=dict,
    )
    renters_responsibilities: Dict[str, str] = Field(
        description="Renters responsibilities and obligations, specifically regarding inside and outside maintenance, repairs, and what they include, and any other duties outlined in the contract",
        default_factory=dict,
    )

    @classmethod
    def get_prompt_description(cls) -> str:
        """Generate the description bullet points for the prompt"""
        # Get unique descriptions to avoid duplication
        unique_descriptions = set()
        for field_info in cls.model_fields.values():
            unique_descriptions.add(field_info.description)

        # Format as bullet points
        bullet_points = [f"    - {desc}" for desc in sorted(unique_descriptions)]
        return "\n".join(bullet_points)

    @classmethod
    def get_example_json(cls) -> str:
        """Generate example JSON for prompt"""
        example = cls(
            landlord="John Doe",
            tenant="Maria Smith",
            monthly_rental_amount="3000 DKK",
            payment_terms="First of each month",
            rental_type="Ejerlejlighed",
            property_address="Street 123, City, ZIP",
            lease_start_date="2023-01-01",
            lease_duration="12 months",
            termination_conditions="3 months notice",
            price_adjustments="Rent can be adjusted annually based on CPI",
            deposit_amount="6000 DKK",
            prepaid_rent="3000 DKK",
            amenities="Parking, Dishwasher",
            utilities={
                "heating": "Included",
                "water": "Included",
                "electricity": "Included",
                "internet": "Included",
            },
            renters_responsibilities={
                "inside_maintenance": "Tenant is responsible for all inside maintenance",
                "outside_maintenance": "Landlord is responsible for outside maintenance",
                "repairs": "Tenant must report all repairs needed",
            },
        )
        return example.model_dump_json(indent=2)


def parse_contract_pdf_to_text(file_path: str) -> str:
    pages = convert_from_path(
        file_path,
        poppler_path=r"C:\Projects\poppler-25.07.0\Library\bin",
    )
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page)
    return text


def extract_contract_info(contract_text: str) -> ContractInfo:
    """Extract key information from a rental contract using an LLM"""

    # Create Pydantic output parser
    parser = PydanticOutputParser(pydantic_object=ContractInfo)

    prompt_contract_all_info = f"""
    You are a helpful assistant that summarizes rental contracts.
    Extract the main information from the rental contract below. Focus on key details such as:
    {ContractInfo.get_prompt_description()}

    {{format_instructions}}

    Always include all required fields, even if the information is not explicitly stated in the contract (use "Not specified" for missing values).

    Contract text:
    {{contract_text}}
    """

    llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0)

    prompt_template = PromptTemplate(
        template=prompt_contract_all_info,
        input_variables=["contract_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt_template,
    )

    # Get the raw output and parse with Pydantic
    raw_output = llm_chain.run(contract_text=contract_text)
    result = parser.parse(raw_output)

    return result


def load_contract_and_extract_info(file_path: str) -> ContractInfo:
    contract_text = parse_contract_pdf_to_text(file_path)
    contract_info = extract_contract_info(contract_text)
    return contract_info
