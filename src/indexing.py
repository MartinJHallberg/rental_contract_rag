
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
import re


CHAPTER_REGEX = r"(Kapitel \d+)\n"
PARAGRAPH_REGEX = r"((?:\x0c|(?<=[\w\.]\n))§ \d{1,3}\.)"


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

def split_doc_by_regex(doc:Document,regex_pattern: str)-> list[Document]:
    text = doc.page_content
    splits = re.split(regex_pattern, text)  # Capturing group includes the separator
    chunks = []
    for i in range(1, len(splits), 2):
        heading = splits[i]
        content = splits[i+1] if i+1 < len(splits) else ""
        content = content.strip()
        heading = heading.strip()
        chunk = heading + " " + content
        chunks.append(Document(page_content=chunk, metadata={"heading": heading}))
    
    return chunks

def read_and_split_document_by_chapter(file_path: str)-> list[Document]:
    documents = load_pdf_single(file_path)
    chapters = split_doc_by_regex(documents[0], CHAPTER_REGEX)
    return chapters


def read_and_split_document_by_paragraph(chapters: list[Document])-> list[Document]:
    paragraphs = [split_doc_by_regex(doc, PARAGRAPH_REGEX) for doc in chapters]

    paragraphs = [para for sublist in paragraphs for para in sublist]  # Flatten the list
    
    return paragraphs