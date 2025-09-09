from indexing import split_doc_by_regex, CHAPTER_REGEX, PARAGRAPH_REGEX
from langchain.schema import Document

def test_chapter_split_by_regex():
    content = """Kapitel 1 \n § 1. Something about renting.\n § 2. Something about renting again. \n
    Kapitel 2 \n § 3. More renting stuff.\n § 4. Even more renting stuff."""

    doc = Document(
        page_content=content,
        metadata={}
    )
 
    chunks = split_doc_by_regex(doc, CHAPTER_REGEX)
    
    assert len(chunks) == 2
    assert chunks[0].page_content == "Kapitel 1 § 1. Something about renting.\n § 2. Something about renting again."
    assert chunks[0].metadata["heading"] == "Kapitel 1"
    assert chunks[1].page_content == "Kapitel 2 § 3. More renting stuff.\n § 4. Even more renting stuff."
    assert chunks[1].metadata["heading"] == "Kapitel 2"


def test_paragraph_split_by_regex():
    content = """Kapitel 1\n§ 1. Something about renting.\n§ 2. Something about renting again.\n§ 3. More renting stuff.\n§ 4. Even more renting stuff."""

    doc = Document(
        page_content=content,
        metadata={}
    )

    chunks = split_doc_by_regex(doc, PARAGRAPH_REGEX)

    assert len(chunks) == 4
    assert chunks[0].page_content == "§ 1. Something about renting."
    assert chunks[0].metadata["heading"] == "§ 1."
    assert chunks[1].page_content == "§ 2. Something about renting again."
    assert chunks[1].metadata["heading"] == "§ 2."
    assert chunks[2].page_content == "§ 3. More renting stuff."
    assert chunks[2].metadata["heading"] == "§ 3."
    assert chunks[3].page_content == "§ 4. Even more renting stuff."
    assert chunks[3].metadata["heading"] == "§ 4."