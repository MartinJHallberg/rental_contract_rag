from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import BasePromptTemplate


class SimpleRAGChain:
    def __init__(
        self,
        retriever: VectorStoreRetriever,
        llm: BaseLanguageModel,
        prompt: BasePromptTemplate,
    ):
        self.retriever = retriever
        self.llm = llm
        self.prompt = prompt
        self._chain = self._build_chain()

    def _build_chain(self):
        """Build the RAG chain"""
        return (
            {
                "context": self.retriever | self._format_docs,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def _format_docs(self, docs):
        """Format retrieved documents"""
        return "\n\n".join(doc.page_content for doc in docs)

    def invoke(self, question: str) -> str:
        """Run the RAG chain with a question"""
        return self._chain.invoke(question)
