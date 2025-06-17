# main.py
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import base64
import json
from vector_db import VectorDatabase
import os

app = FastAPI(
    title="TDS Virtual TA",
    description="Automated Teaching Assistant for IIT Madras Online Degree in Data Science",
    version="1.0"
)

# Load the vector database
db = VectorDatabase()
if os.path.exists("tds_vector_db.index"):
    db.load("tds_vector_db")
else:
    raise RuntimeError("Vector database not found. Please build it first.")

class Link(BaseModel):
    url: str
    text: str

class QuestionRequest(BaseModel):
    question: str
    image: Optional[str] = None  # base64 encoded image

class AnswerResponse(BaseModel):
    answer: str
    links: List[Link]

def generate_answer(question: str, context_docs: List[Dict]) -> str:
    """Generate an answer using the context documents."""
    # Simple implementation - can be replaced with LLM
    context = "\n\n".join([doc["content"] for doc in context_docs])
    return f"Based on the course materials:\n\n{context[:2000]}..."

@app.post("/api/", response_model=AnswerResponse)
async def answer_question(request: QuestionRequest):
    try:
        # Search for relevant documents
        results = db.search(request.question, k=3)
        
        # Generate answer (simplified - you might want to use an LLM here)
        answer = generate_answer(request.question, results)
        
        # Prepare links
        links = [
            Link(
                url=doc["source_url"],
                text=doc["content"][:100] + "..."
            )
            for doc in results
        ]
        
        return AnswerResponse(
            answer=answer,
            links=links
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)