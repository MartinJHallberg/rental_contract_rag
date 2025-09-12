from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from pdf2image import convert_from_path
import pytesseract
from pathlib import Path

from pydantic import BaseModel, Field
from typing import Dict, Optional
from langchain.output_parsers import PydanticOutputParser
import os
import hashlib
import json
from config import CACHE_DIR, LLM_MODEL, LLM_TEMPERATURE


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


class RentalContract(BaseModel):
    """Pydantic model for rental contract. Created to allow for caching of LLM calls"""

    text: str = Field(description="Full text of the rental contract")
    file_name: str = Field(description="File name of the contract")


def parse_contract_pdf_to_text(file_path: str) -> RentalContract:
    """Parse a PDF rental contract to text using OCR"""

    # Ensure cache directory exists
    cache_dir = CACHE_DIR
    os.makedirs(cache_dir, exist_ok=True)

    # Create a unique cache key based on file path
    cache_key_str = f"pdf_parse:{file_path}"
    cache_key_hash = hashlib.sha256(cache_key_str.encode("utf-8")).hexdigest()
    cache_file_path = os.path.join(cache_dir, f"{cache_key_hash}.json")

    # Try to load from cache
    if os.path.exists(cache_file_path):
        with open(cache_file_path, "r", encoding="utf-8") as f:
            cached_data = json.load(f)
        return RentalContract(**cached_data)

    # If not in cache, process the PDF
    pages = convert_from_path(
        file_path,
    )
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page)

    # Save to cache
    with open(cache_file_path, "w", encoding="utf-8") as f:
        json.dump(
            {"text": text, "file_name": Path(file_path).name},
            f,
            ensure_ascii=False,
            indent=2,
        )

    return RentalContract(text=text, file_name=Path(file_path).name)


def extract_contract_info(rental_contract: RentalContract) -> ContractInfo:
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

    llm = ChatOpenAI(model_name=LLM_MODEL, temperature=LLM_TEMPERATURE)

    prompt_template = PromptTemplate(
        template=prompt_contract_all_info,
        input_variables=["contract_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt_template,
    )

    # Ensure cache directory exists
    cache_dir = CACHE_DIR
    os.makedirs(cache_dir, exist_ok=True)

    # Create a unique cache key based on file name and prompt
    cache_key_str = (
        f"contract_info_{rental_contract.file_name}:{prompt_contract_all_info}"
    )
    cache_key_hash = hashlib.sha256(cache_key_str.encode("utf-8")).hexdigest()
    cache_file_path = os.path.join(cache_dir, f"{cache_key_hash}.json")

    # Try to load from cache
    if os.path.exists(cache_file_path):
        with open(cache_file_path, "r", encoding="utf-8") as f:
            cached_data = json.load(f)
        return ContractInfo(**cached_data)

    # Get the raw output and parse with Pydantic
    raw_output = llm_chain.run(contract_text=rental_contract.text)
    result = parser.parse(raw_output)

    # Save to cache
    with open(cache_file_path, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)

    return result


def load_contract_and_extract_info(file_path: str) -> ContractInfo:
    contract = parse_contract_pdf_to_text(file_path)
    contract_info = extract_contract_info(contract)
    return contract_info
