from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
import re


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
