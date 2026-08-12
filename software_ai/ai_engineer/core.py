import os
import chromadb
from sentence_transformers import SentenceTransformer
import shutil
import torch

#set the path of the knowledges directory
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledges")
EMBEDDER_MODEL_NAME = 'all-MiniLM-L6-v2'
DATABASE_PATH = "./database"
KNOWLEDGE_BASE_COLLECTION_NAME = "jarvis"

#if we have gpu, we want to use it for the embedding model, otherwise we will use cpu
device = "cuda" if torch.cuda.is_available() else "cpu"

#initalize the embedding model
embedder = SentenceTransformer(EMBEDDER_MODEL_NAME, device=device)

#delete the existing database if it exists
if os.path.exists(DATABASE_PATH):
    print(f"Deleting existing database at {DATABASE_PATH}")
    shutil.rmtree(DATABASE_PATH)

#initalize the ChromaDB client
client = chromadb.PersistentClient(path=DATABASE_PATH)

#create a collection for the knowledge base
collection = client.create_collection(KNOWLEDGE_BASE_COLLECTION_NAME)

#a function to load in all the knowledge files:
def load_knowledge_files():
    # a empty list to hold all documents
    documents = []

    # go through all documents in the knowledge directory
    for filename in os.listdir(KNOWLEDGE_DIR):
        file_path = os.path.join(KNOWLEDGE_DIR, filename)
        print(f"Loading knowledge file: {filename} from {file_path}")

        #open the file and read it then add it to the documents list
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()

            #build the knowledge structure
            knowledge = {
                "id": filename,
                "content": content,
                "source": file_path
            }

            #add to the documents list
            documents.append(knowledge)

    #build the embeddings for the documents and add them to the collection
    
    # -----------------------------
    # Prepare batch
    # -----------------------------

    contents = [
        document["content"]
        for document in documents
    ]

    ids = [
        document["id"]
        for document in documents
    ]

    sources = [
        document["source"]
        for document in documents
    ]


    print(
        f"\nGenerating embeddings for "
        f"{len(contents)} documents..."
    )


    # -----------------------------
    # Generate embeddings on GPU
    # -----------------------------

    vectors = embedder.encode(
        contents,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True
    ).tolist()


    # -----------------------------
    # Add everything to Chroma
    # -----------------------------

    collection.add(
        ids=ids,
        documents=contents,
        embeddings=vectors,
        metadatas=[
            {"source": source}
            for source in sources
        ]
    )

    #show the document was loaded
    for id, source in zip(ids, sources):
        print(f"Loaded knowledge file: {id} from {source}")


if __name__ == "__main__":
    load_knowledge_files()