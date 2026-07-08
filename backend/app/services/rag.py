import numpy as np
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeDocument
from app.services.ai import ai_service
from typing import List, Dict, Any

def retrieve_context(db: Session, query: str, limit: int = 3, category_filter: str = None) -> List[Dict[str, Any]]:
    """
    RAG utility to search matching knowledge document chunks.
    Calculates cosine similarity in Python using NumPy over L2-normalized embeddings.
    """
    query_embedding = ai_service.get_embeddings(query)
    q_vec = np.array(query_embedding)
    
    # Query database for candidates
    query_builder = db.query(KnowledgeDocument)
    
    # Optional category filter
    if category_filter:
        # Check matching metadata
        query_builder = query_builder.filter(
            KnowledgeDocument.metadata_info["department"].astext == category_filter
        )
        
    docs = query_builder.all()
    
    results = []
    for doc in docs:
        if not doc.embedding:
            continue
        
        d_vec = np.array(doc.embedding)
        # Cosine similarity (dot product of L2 normalized vectors)
        similarity = float(np.dot(q_vec, d_vec))
        
        results.append((similarity, doc))
        
    # Sort by similarity score descending
    results.sort(key=lambda x: x[0], reverse=True)
    
    retrieved_items = []
    for score, doc in results[:limit]:
        retrieved_items.append({
            "score": score,
            "id": doc.id,
            "title": doc.title,
            "content": doc.content_chunk,
            "source": doc.source_uri,
            "version": doc.version,
            "date": doc.publication_date.isoformat() if doc.publication_date else None,
            "metadata": doc.metadata_info
        })
        
    return retrieved_items

def generate_policy_response(db: Session, query: str, limit: int = 3) -> Dict[str, Any]:
    """
    Retrieve context and construct an explainable RAG prompt for the Policy Support Agent.
    """
    context_list = retrieve_context(db, query, limit=limit)
    
    if not context_list:
        return {
            "answer": "No relevant verified government policy or SOP documents could be retrieved. I cannot answer this without verified context.",
            "sources": []
        }
        
    # Build RAG Context
    context_str = ""
    for idx, item in enumerate(context_list, 1):
        context_str += f"\n[{idx}] SOURCE: {item['title']} (v{item['version']}, Date: {item['date']})\nCONTENT: {item['content']}\n"
        
    # Simple prompt constructing for RAG
    # We will simulate or call LLM to answer using this context
    # If LLM key is not active, mock an answer derived from the context
    answer = ""
    if ai_service.client:
        try:
            response = ai_service.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are the Governance Policy Intelligence Agent. You must answer the user's query using ONLY the provided verified context. You must cite your sources (e.g. '[1]') directly. Do not invent facts."
                    },
                    {
                        "role": "user", 
                        "content": f"Context Documents:\n{context_str}\n\nUser Query: {query}"
                    }
                ]
            )
            answer = response.choices[0].message.content
        except Exception as e:
            print(f"RAG prompt failed, falling back: {e}")
            
    if not answer:
        # Fallback to realistic response constructed directly from the seeded documents
        best_match = context_list[0]
        answer = f"Based on the verified policy '{best_match['title']}' (version {best_match['version']}, published {best_match['date']}): {best_match['content'][:250]}..."
        
    return {
        "answer": answer,
        "sources": context_list
    }
