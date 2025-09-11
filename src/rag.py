from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import VectorStoreRetriever, InMemoryVectorStore
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import BasePromptTemplate
from contract_loader import ContractInfo
from langchain_community.chat_models import ChatOpenAI
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain_openai.embeddings import OpenAIEmbeddings


from data_loading import (
    read_and_split_document_by_chapter,
    read_and_split_document_by_paragraph,
)


def create_rental_law_retriever(
    file_path: str, embedding_model, k: int = 5
) -> VectorStoreRetriever:
    """Create a retriever for rental law documents"""
    chapters = read_and_split_document_by_chapter(file_path)
    paragraphs = read_and_split_document_by_paragraph(chapters)

    vector_store = InMemoryVectorStore.from_documents(
        documents=paragraphs,
        embedding=embedding_model,
    )

    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})


class DocumentFormatter:
    @staticmethod
    def simple_format(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    @staticmethod
    def detailed_format(docs):
        # Include metadata...
        pass


class ValidationOutput(BaseModel):
    to_be_checked: bool = Field(
        description="Answer with 'true' if the contract is valid, otherwise 'false'"
    )
    explanation: str = Field(description="Explanation of the validation result")
    reference: dict[str:str] = Field(
        description="List of relevant paragraphs (and which page they can be found) from the contract that support the validation result"
    )


class RAGChain:
    def __init__(
        self,
        retriever: VectorStoreRetriever,
        prompt: BasePromptTemplate,
        llm: BaseLanguageModel = ChatOpenAI(model="gpt-4", temperature=0),
        document_formatter: DocumentFormatter = DocumentFormatter.simple_format,
        output_parser: PydanticOutputParser = PydanticOutputParser(
            pydantic_object=ValidationOutput
        ),
    ):
        self.retriever = retriever
        self.llm = llm
        self.prompt = prompt
        self.document_formatter = document_formatter
        self._chain = self._build_chain()
        self.output_parser = output_parser

    @classmethod
    def create_with_rental_law_retriever(
        cls,
        prompt: BasePromptTemplate,
        file_path: str = "src/data/lejeloven_2025.pdf",
        embedding_model=OpenAIEmbeddings(),
        k: int = 5,
        **kwargs,
    ):
        if embedding_model is None:
            embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
        retriever = create_rental_law_retriever(file_path, embedding_model, k)
        return cls(retriever=retriever, prompt=prompt, **kwargs)

    def _build_chain(self):
        """Build the RAG chain"""
        return (
            {
                "context": self.retriever | self._format_docs,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
            | self.output_parser
        )

    def _format_docs(self, docs):
        """Format retrieved documents"""
        return self.document_formatter(docs)

    def invoke(self, question: str) -> str:
        """Run the RAG chain with a question"""
        return self._chain.invoke(question)


def validate_deposit_amount(
    rag_chain: RAGChain,
    contract_info: ContractInfo,
) -> ValidationOutput:
    """Validate if the deposit amount extracted is a valid number"""

    try:
        deposit_amount = contract_info.deposit_amount
        monthly_rental_amount = contract_info.monthly_rental_amount
        answer = rag_chain.invoke(
            f"Is the deposit amount '{deposit_amount}' a valid number and does it not exceed three times the monthly rental amount '{monthly_rental_amount}'?"
        )

        return answer

    except Exception as e:
        print(f"Error during validation: {e}")
        answer = ValidationOutput(
            to_be_checked=False,
            explanation="An error occurred during validation.",
            reference={"error": str(e)},
        )
        return answer
