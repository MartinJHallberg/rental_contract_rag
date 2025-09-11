from rag import RAGChain


if __name__ == "__main__":
    rag_chain = RAGChain()

    response = rag_chain.ask("What is the maximum deposit allowed for a residential rental agreement?")
    print("Response:", response)