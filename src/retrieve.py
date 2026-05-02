from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("intfloat/multilingual-e5-large")
client = chromadb.PersistentClient(path="./vectorstore")
collection = client.get_or_create_collection("laws")

def retrieve(query, top_k=5):
    embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=embedding, n_results=top_k)
    
    docs = results["documents"][0]
    metadatas = results["metadatas"][0]
    return list(zip(docs, metadatas))