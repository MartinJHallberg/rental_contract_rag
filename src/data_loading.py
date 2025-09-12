from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
import re
from langchain_chroma import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever
from config import VECTOR_STORE_DIR, EMBEDDING_MODEL, COLLECTION_NAME

CHAPTER_REGEX = r"(Kapitel \d+)\n"
PARAGRAPH_REGEX = r"((?:^|\x0c|(?<=[\w\.]\n))§ \d{1,3}\.)"  # Matches "§ 1.", "§ 23." at start of line or after a form feed or after a newline


def load_pdf_single(file_path: str) -> list[Document]:
    loader = PyPDFLoader(file_path, mode="single")
    documents = loader.load()
    return documents


def load_pdf_by_page(file_paths: str) -> list[Document]:
    loader = PyPDFLoader(
        file_paths,
    )
    documents = loader.load()
    return documents


def split_doc_by_regex(doc: Document, regex_pattern: str) -> list[Document]:
    text = doc.page_content
    parent_title = doc.metadata.get("title", "")
    splits = re.split(regex_pattern, text)  # Capturing group includes the separator
    chunks = []
    for i in range(1, len(splits), 2):
        title = splits[i]
        content = splits[i + 1] if i + 1 < len(splits) else ""
        content = content.strip()
        title = title.strip()
        chunk = title + " " + content
        chunks.append(
            Document(
                page_content=chunk,
                metadata={"title": title, "parent_title": parent_title},
            )
        )

    return chunks


def read_and_split_document_by_chapter(file_path: str) -> list[Document]:
    documents = load_pdf_single(file_path)
    chapters = split_doc_by_regex(documents[0], CHAPTER_REGEX)
    return chapters


def read_and_split_document_by_paragraph(chapters: list[Document]) -> list[Document]:
    paragraphs = [split_doc_by_regex(doc, PARAGRAPH_REGEX) for doc in chapters]

    paragraphs = [
        para for sublist in paragraphs for para in sublist
    ]  # Flatten the list

    return paragraphs


def extract_paragraphs_from_page(doc: Document, regex_pattern: str) -> dict[int, int]:
    paragraphs = re.findall(regex_pattern, doc.page_content)

    page_paragraph = {
        int(re.findall(r"\d{1,3}", para)[0]): doc.metadata["page"]
        for para in paragraphs
    }
    return page_paragraph


def add_page_numbers_to_paragraphs(
    paragraphs: list[Document], documents: list[Document], regex: str
) -> list[Document]:
    paragraph_pages = [extract_paragraphs_from_page(doc, regex) for doc in documents]
    paragraph_pages = {
        k: v for d in paragraph_pages for k, v in d.items()
    }  # unnest list

    for para in paragraphs:
        para_number = int(re.findall(r"\d{1,3}", para.metadata["title"])[0])
        para.metadata["page"] = paragraph_pages.get(para_number, None)

    return paragraphs


def build_rental_law_collection(
    file_path: str = "src/data/lejeloven_2025.pdf",
    collection_name: str = COLLECTION_NAME,
    embedding_model: str = EMBEDDING_MODEL,
    force_rebuild: bool = False,
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
                persist_directory=persist_directory,
            )
            if existing_db._collection.count() > 0:
                print(
                    f"Collection '{collection_name}' already exists. Use force_rebuild=True to recreate."
                )
                return
        except Exception as e:
            print(f"Error loading collection '{collection_name}': {e}")
            print(f"Building document collection '{collection_name}'...")

            # Process documents
            embeddings = OpenAIEmbeddings(model=embedding_model)
            chapters = read_and_split_document_by_chapter(file_path)
            paragraphs = read_and_split_document_by_paragraph(chapters)

            # Create Chroma vector store
            VECTOR_STORE_DIR.mkdir(exist_ok=True, parents=True)
            Chroma.from_documents(
                documents=paragraphs,
                embedding=embeddings,
                collection_name=collection_name,
                persist_directory=persist_directory,
            )

            print(f"Document collection saved to {persist_directory}")
            print(f"Total documents: {len(paragraphs)}")


def load_rental_law_retriever(
    collection_name: str = COLLECTION_NAME,
    embedding_model: str = EMBEDDING_MODEL,
    k: int = 5,
    force_rebuild: bool = False,
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
            persist_directory=persist_directory,
        )

        # Check if collection has documents
        if vector_store._collection.count() == 0:
            raise ValueError("Collection is empty")

    except Exception:
        print(f"Collection '{collection_name}' not found. Building it now...")
        build_rental_law_collection()

        # Load the newly created collection
        embeddings = OpenAIEmbeddings(model=embedding_model)
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory,
        )

    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})
