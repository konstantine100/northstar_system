import os
import chromadb
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

def ingest_documents(docs_dir: str, db_dir: str):
    print(f"Loading documents from {docs_dir}...")
    documents = []
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        print(f"Directory {docs_dir} does not exist.")
        return
        
    for file in docs_path.iterdir():
        try:
            if file.suffix.lower() == '.pdf':
                loader = PyPDFLoader(str(file))
                documents.extend(loader.load())
            elif file.suffix.lower() == '.docx':
                loader = Docx2txtLoader(str(file))
                documents.extend(loader.load())
            elif file.suffix.lower() == '.txt':
                loader = TextLoader(str(file))
                documents.extend(loader.load())
        except Exception as e:
            print(f"Failed to load {file.name}: {e}")
    
    print(f"Loaded {len(documents)} document fragments.")
    
    if len(documents) == 0:
        print("No documents found. Skipping vector DB creation.")
        return
        
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")
    
    client = chromadb.PersistentClient(path=db_dir)
    collection = client.get_or_create_collection(name="hr_policies")
    
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    ids = [f"doc_{i}" for i in range(len(chunks))]
    
    print("Generating embeddings...")
    embeddings = model.encode(texts).tolist()
    
    print("Saving to ChromaDB...")
    collection.add(
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )
    print("Ingestion complete!")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(base_dir) # Northstar System folder
    docs_dir = os.path.join(project_root, "documents")
    db_dir = os.path.join(base_dir, "chroma_db")
    ingest_documents(docs_dir, db_dir)
