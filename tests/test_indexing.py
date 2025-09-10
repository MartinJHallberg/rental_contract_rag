from indexing import (
    read_and_split_document_by_paragraph,
    split_doc_by_regex,
    CHAPTER_REGEX,
    PARAGRAPH_REGEX,
    read_and_split_document_by_chapter,
    read_and_split_document_by_paragraph
)

from langchain.schema import Document

def test_chapter_split_by_regex():
    content = """Kapitel 1\n § 1. Something about renting.\n § 2. Something about renting again. \n
    Kapitel 2\n § 3. More renting stuff.\n § 4. Even more renting stuff."""

    doc = Document(
        page_content=content,
        metadata={}
    )
 
    chunks = split_doc_by_regex(doc, CHAPTER_REGEX)
    
    assert len(chunks) == 2
    assert chunks[0].page_content == "Kapitel 1 § 1. Something about renting.\n § 2. Something about renting again."
    assert chunks[0].metadata["title"] == "Kapitel 1"
    assert chunks[1].page_content == "Kapitel 2 § 3. More renting stuff.\n § 4. Even more renting stuff."
    assert chunks[1].metadata["title"] == "Kapitel 2"


def test_paragraph_split_by_regex():
    content = """Kapitel 1\n§ 1. Something about renting.\n§ 2. Something about renting again.\n§ 3. More renting stuff.\n§ 4. Even more renting stuff."""

    doc = Document(
        page_content=content,
        metadata={}
    )

    chunks = split_doc_by_regex(doc, PARAGRAPH_REGEX)

    assert len(chunks) == 4
    assert chunks[0].page_content == "§ 1. Something about renting."
    assert chunks[0].metadata["title"] == "§ 1."
    assert chunks[1].page_content == "§ 2. Something about renting again."
    assert chunks[1].metadata["title"] == "§ 2."
    assert chunks[2].page_content == "§ 3. More renting stuff."
    assert chunks[2].metadata["title"] == "§ 3."
    assert chunks[3].page_content == "§ 4. Even more renting stuff."
    assert chunks[3].metadata["title"] == "§ 4."

def test_read_all_chapters():
    from indexing import read_and_split_document_by_chapter
    file_path = "src/data/lejeloven_2025.pdf"
    chunks = read_and_split_document_by_chapter(file_path)
    chapter_numbers = [f"Kapitel {i}" for i in range(1, len(chunks)+1)]
    extracted_headings = [chunk.metadata["title"] for chunk in chunks]
    assert chapter_numbers == extracted_headings
    assert len(chunks) == 29 #check that we have 29 chapters in the document

    
def test_extract_all_paragraphs():

    file_path = "src/data/lejeloven_2025.pdf"
    chapters = read_and_split_document_by_chapter(file_path)
    paragraphs = read_and_split_document_by_paragraph(chapters)
    paragraphs_numbers = [f"§ {i}." for i in range(1, len(paragraphs)+1)]
    extracted_headings = [chunk.metadata["title"] for chunk in paragraphs]
    missing_headings = set(paragraphs_numbers) - set(extracted_headings)

    assert paragraphs_numbers == extracted_headings
    assert len(paragraphs) == 213  #check that we have 212 paragraphs in the document

    # Check that chapter titles are correctly assigned as parent titles
    chapter_numbers = [f"Kapitel {i}" for i in range(1, len(chapters)+1)]

    parent_titles = [chunk.metadata["parent_title"] for chunk in paragraphs]
    assert all(title in chapter_numbers for title in parent_titles)


def test_page_to_paragraph_mapping():
    from indexing import load_pdf_by_page, add_page_numbers_to_paragraphs, read_and_split_document_by_paragraph
    file_path = "src/data/lejeloven_2025.pdf"
    documents = load_pdf_by_page(file_path)
    chapters = read_and_split_document_by_chapter(file_path)
    paragraphs = read_and_split_document_by_paragraph(chapters)
    paragraphs_with_page_numbers = add_page_numbers_to_paragraphs(paragraphs, documents, PARAGRAPH_REGEX)

    # Check that each paragraph now has a page number in its metadata
    for para in paragraphs_with_page_numbers:
        assert "page" in para.metadata
        assert isinstance(para.metadata["page"], int)

    # Check that page numbers are increasing by paragraph
    page_numbers = [para.metadata["page"] for para in paragraphs_with_page_numbers]
    assert page_numbers == sorted(page_numbers)
