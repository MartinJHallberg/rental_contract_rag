
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document


def load_pdf_single(file_path: str)-> list[Document]:
    loader = PyPDFLoader(
        file_path,
        mode="single"
)
    documents = loader.load()
    return documents

def load_pdf_by_page(file_paths: str)-> list[Document]:

    loader = PyPDFLoader(
        file_paths,
)
    documents = loader.load()
    return documents
