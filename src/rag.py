from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import (
    VectorStoreRetriever,
    InMemoryVectorStore
    )
from langchain_community.vectorstores import Chroma
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

from pathlib import Path
# Import configuration (this automatically sets up LangSmith)
from config import VECTOR_STORE_DIR, EMBEDDING_MODEL, COLLECTION_NAME

def build_rental_law_collection(
    file_path: str = "src/data/lejeloven_2025.pdf",
    collection_name: str = COLLECTION_NAME,
    embedding_model: str = EMBEDDING_MODEL,
    force_rebuild: bool = False
):
    """Build a persistent document collection using Chroma"""
    
    persist_directory = str(VECTOR_STORE_DIR)
    
    # Check if collection exists
    if not force_rebuild:
        try:
            embeddings = OpenAIEmbeddings(model=embedding_model)
            existing_db = Chroma(
                collection_name=collection_name,
                embedding_function=embeddings,
                persist_directory=persist_directory
            )
            if existing_db._collection.count() > 0:
                print(f"Collection '{collection_name}' already exists. Use force_rebuild=True to recreate.")
                return
        except:
            pass  # Collection doesn't exist, continue with creation
    
    print(f"Building document collection '{collection_name}'...")
    
    # Process documents
    embeddings = OpenAIEmbeddings(model=embedding_model)
    chapters = read_and_split_document_by_chapter(file_path)
    paragraphs = read_and_split_document_by_paragraph(chapters)
    
    # Create Chroma vector store
    VECTOR_STORE_DIR.mkdir(exist_ok=True, parents=True)
    vector_store = Chroma.from_documents(
        documents=paragraphs,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory
    )
    
    print(f"Document collection saved to {persist_directory}")
    print(f"Total documents: {len(paragraphs)}")


def load_rental_law_retriever(
    collection_name: str = COLLECTION_NAME,
    embedding_model: str = EMBEDDING_MODEL,
    k: int = 5,
    force_rebuild: bool = False
) -> VectorStoreRetriever:
    """Load an existing document collection"""

    persist_directory = str(VECTOR_STORE_DIR)  # Same as build function
    
    if force_rebuild:
        print(f"Force rebuilding collection '{collection_name}'...")
        build_rental_law_collection(force_rebuild=True)
    
    try:
        print(f"Loading document collection '{collection_name}'...")
        embeddings = OpenAIEmbeddings(model=embedding_model)
        
        # Use Chroma constructor, not load_local
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory
        )
        
        # Check if collection has documents
        if vector_store._collection.count() == 0:
            raise ValueError("Collection is empty")
            
    except Exception as e:
        print(f"Collection '{collection_name}' not found. Building it now...")
        build_rental_law_collection()
        
        # Load the newly created collection
        embeddings = OpenAIEmbeddings(model=embedding_model)
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory
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
        self.retriever = retriever or load_rental_law_retriever()
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
