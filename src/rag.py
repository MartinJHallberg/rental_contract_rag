from langchain_core.runnables import RunnablePassthrough
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from contract_loader import ContractInfo
from config import LLM_MODEL, LLM_TEMPERATURE
from data_loading import load_rental_law_retriever
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser


def format_docs(docs):
    """Simple document formatter"""
    return "\n\n".join(doc.page_content for doc in docs)


class LLMOutput(BaseModel):
    """Output schema for LLM answers with integrated prompt"""

    should_be_checked: bool = Field(
        description="Whether the issue should be checked further"
    )
    description: str = Field(description="Description of the issue")
    references: dict[str, str] = Field(
        description="Reference to paragraph and page number", default_factory=dict
    )

    @classmethod
    def get_parser(cls) -> PydanticOutputParser:
        """Get the output parser for this model"""
        return PydanticOutputParser(pydantic_object=cls)

    @classmethod
    def get_prompt(cls) -> ChatPromptTemplate:
        """Get the prompt template for this output format"""
        parser = cls.get_parser()

        template = """You are a legal expert on Danish rental law. Based on the provided context, analyze the question and provide a structured response.

Context: {context}

Question: {question}

{format_instructions}

Important guidelines:
- Set should_be_checked to true if the issue does not comply with Danish rental law or if you are unsure
- Set should_be_checked to false if the answer is clearly legal and compliant with Danish rental law
- Provide concise and relevant descriptions of the information you have retrieved and why the contract information complies or does not comply with the law
- Include references to specific paragraphs and page numbers from the context in the references field in the format {{"paragraph": "page number"}}
"""

        return ChatPromptTemplate.from_template(
            template,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )


class RAGChain:
    """Simple RAG chain for asking questions about rental law"""

    def __init__(
        self,
        retriever: VectorStoreRetriever = None,
        llm: BaseLanguageModel = None,
        llm_output: LLMOutput = None,
    ):
        self.retriever = retriever or load_rental_law_retriever()
        self.llm = llm or ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)

        if llm_output is None:
            self.output_parser = LLMOutput.get_parser()
            self.prompt = LLMOutput.get_prompt()
        else:
            self.output_parser = llm_output.get_parser()
            self.prompt = llm_output.get_prompt()

        self._chain = self._build_chain()

    def _build_chain(self):
        """Build the RAG chain"""
        return (
            {
                "context": self.retriever | format_docs,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
            | self.output_parser
        )

    def ask(self, question: str) -> LLMOutput | str:
        """Ask a question and get an answer"""
        return self._chain.invoke(question)


# Contract validation functions - pass specific attributes only
def validate_deposit_amount(
    rag_chain: RAGChain, deposit_amount: str, monthly_rental_amount: str
) -> LLMOutput:
    """Check if deposit amount is legal"""
    question = f"Is a deposit of {deposit_amount} legal for a rental property with monthly rent of {monthly_rental_amount}?"
    return rag_chain.ask(question)


def validate_termination_conditions(
    rag_chain: RAGChain, termination_conditions: str
) -> LLMOutput:
    """Check if termination conditions are legal"""
    question = f"Are these termination conditions legal: {termination_conditions}?"
    return rag_chain.ask(question)


def validate_price_adjustments(
    rag_chain: RAGChain, price_adjustments: str
) -> LLMOutput:
    """Check if price adjustment conditions are legal"""
    question = f"Are these price adjustment conditions legal: {price_adjustments}?"
    return rag_chain.ask(question)


def validate_lease_duration(
    rag_chain: RAGChain, lease_duration: str, rental_type: str = "residential"
) -> LLMOutput:
    """Check if lease duration is legal"""
    question = (
        f"Is a lease duration of {lease_duration} legal for a {rental_type} property?"
    )
    return rag_chain.ask(question)


def validate_utilities_responsibility(
    rag_chain: RAGChain, utilities: dict[str, str]
) -> LLMOutput:
    """Check if utility responsibility distribution is legal"""
    utilities_str = ", ".join([f"{util}: {resp}" for util, resp in utilities.items()])
    question = f"Are these utility responsibilities legal: {utilities_str}?"
    return rag_chain.ask(question)


def validate_contract(
    rag_chain: RAGChain, contract_info: ContractInfo
) -> dict[str, LLMOutput]:
    """Validate all aspects of a contract - convenience function"""

    results = {}

    # Validate deposit
    results["deposit"] = validate_deposit_amount(
        rag_chain, contract_info.deposit_amount, contract_info.monthly_rental_amount
    )

    # Validate termination conditions
    results["termination"] = validate_termination_conditions(
        rag_chain, contract_info.termination_conditions
    )

    # Validate price adjustments
    results["price_adjustments"] = validate_price_adjustments(
        rag_chain, contract_info.price_adjustments
    )

    # Validate lease duration
    results["lease_duration"] = validate_lease_duration(
        rag_chain, contract_info.lease_duration, contract_info.rental_type
    )

    # Validate utilities (if applicable)
    if contract_info.utilities:
        results["utilities"] = validate_utilities_responsibility(
            rag_chain, contract_info.utilities
        )

    return results
