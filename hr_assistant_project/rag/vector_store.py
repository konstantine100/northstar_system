import os
import chromadb
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self, db_dir: str):
        self.client = chromadb.PersistentClient(path=db_dir)
        self.collection = self.client.get_or_create_collection(name="hr_policies")
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def search_hr_policy(self, query: str, top_k: int = 3) -> str:
        if self.collection.count() == 0:
            return "ბაზაში არ არის ატვირთული HR პოლიტიკის დოკუმენტები."
            
        query_embedding = self.model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        if not results['documents'] or not results['documents'][0]:
            return "ვერ მოიძებნა შესაბამისი ინფორმაცია პოლიტიკის დოკუმენტებში."
            
        context_parts = []
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            source = meta.get('source', 'Unknown')
            # Extract just the filename for cleaner output
            import os
            source_file = os.path.basename(source)
            context_parts.append(f"წყარო: {source_file}\n{doc}")
            
        return "\n\n".join(context_parts)
