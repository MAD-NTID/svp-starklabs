import os
import chromadb
from sentence_transformers import SentenceTransformer

#set the path of the knowledges directory
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledges")
EMBEDDER_MODEL_NAME = 'all-MiniLM-L6-v2'
DATABASE_PATH = "./database"
KNOWLEDGE_BASE_COLLECTION_NAME = "jarvis"


#initalize the embedding model
embedder = SentenceTransformer(EMBEDDER_MODEL_NAME)

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
    for document in documents:
        content = document["content"]
        id = document["id"]
        source = document["source"]

        vector = embedder.encode(content).tolist()

        collection.add(
            ids=[id],
            documents=[content],
            embeddings=[vector],
            metadatas=[{"source": source}]  
        )

        #show the document was loaded
        print(f"Loaded knowledge file: {id} from {source}")


if __name__ == "__main__":
    load_knowledge_files()