import ollama
import chromadb

from sentence_transformers import SentenceTransformer

EMBEDDER_MODEL_NAME = 'all-MiniLM-L6-v2'
DATABASE_PATH = "../database"
COLLECTION_NAME = "jarvis"
OLLAMA_MODEL_NAME = "llama3.2:latest"


embedder = SentenceTransformer(EMBEDDER_MODEL_NAME)
client = chromadb.PersistentClient(path=DATABASE_PATH)
collection = client.get_collection(COLLECTION_NAME)

"""
This is the instruction to JARVIS.
It tells JARVIS how it should what it should do
and how it should answer user questions using
the knowledges from the documents.
"""
SYSTEM_PROMPT = """
You are JARVIS.

Answer user questions using the provided knowledge.
Be helpful and provide information from the documents.
"""

def retrieve_relevant_documents(question, max_k=3):
    #embed the question
    question_vector = embedder.encode(question).tolist()

    #search the collection for relevant documents
    results = collection.query(
        query_embeddings=[question_vector],
        n_results=max_k
    )

    docs = results["documents"][0]

    #show the retrieved documents
    print(f"Retrieved {len(docs)} relevant documents:")
    # for i, doc in enumerate(docs):
    #     print(f"Document {i+1}: {doc[:50]}...")

    return docs 

def ask(question, max_k=3):

    # relevant documents
    relevant_documents = retrieve_relevant_documents(question, max_k)

    # build the context from the relevant documents
    context = "\n\n".join(relevant_documents)

    # build the prompt for the LLM
    prompt = f"""
        Knowledge:

        {context}


        User Question:

        {question}
    """

    # send the prompt to the LLM
    response = ollama.chat(
        model=OLLAMA_MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        stream = True
    )

    for chunk in response:
        yield chunk["message"]["content"]


#setting up a test
if __name__ == "__main__":
    while True:
        question = input("Ask a question: ")
        if question == "exit" or question == "quit":
            print("Exiting...")
            break
        answer = ask(question)
        print(
            "\nJarvis:",
            answer
        )
