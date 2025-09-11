from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import VectorStoreRetriever, InMemoryVectorStore
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import BasePromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from contract_loader import ContractInfo
from data_loading import (
    read_and_split_document_by_chapter,
    read_and_split_document_by_paragraph,
)
from langchain import hub


def create_rental_law_retriever(
    file_path: str = "src/data/lejeloven_2025.pdf", 
    k: int = 5
) -> VectorStoreRetriever:
    """Create a retriever for rental law documents"""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    chapters = read_and_split_document_by_chapter(file_path)
    paragraphs = read_and_split_document_by_paragraph(chapters)

    vector_store = InMemoryVectorStore.from_documents(
        documents=paragraphs,
        embedding=embeddings,
    )

    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})


def format_docs(docs):
    """Simple document formatter"""
    return "\n\n".join(doc.page_content for doc in docs)


class RAGChain:
    """Simple RAG chain for asking questions about rental law"""
    
    def __init__(
        self,
        prompt: BasePromptTemplate=None,
        retriever: VectorStoreRetriever = None,
        llm: BaseLanguageModel = None,
    ):
        self.retriever = retriever or create_rental_law_retriever()
        self.llm = llm or ChatOpenAI(model="gpt-4", temperature=0)
        self.prompt = prompt or hub.pull("rlm/rag-prompt")
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
            | StrOutputParser()
        )

    def ask(self, question: str) -> str:
        """Ask a question and get an answer"""
        return self._chain.invoke(question)


# Contract validation functions
def validate_deposit_amount(rag_chain: RAGChain, contract_info: ContractInfo) -> str:
    """Check if deposit amount is legal"""
    question = f"Is a deposit of {contract_info.deposit_amount} legal for a rental property with monthly rent of {contract_info.monthly_rental_amount}?"
    return rag_chain.ask(question)


def validate_termination_conditions(rag_chain: RAGChain, contract_info: ContractInfo) -> str:
    """Check if termination conditions are legal"""
    question = f"Are these termination conditions legal: {contract_info.termination_conditions}?"
    return rag_chain.ask(question)


def validate_price_adjustments(rag_chain: RAGChain, contract_info: ContractInfo) -> str:
    """Check if price adjustment conditions are legal"""
    question = f"Are these price adjustment conditions legal: {contract_info.price_adjustments}?"
    return rag_chain.ask(question)
