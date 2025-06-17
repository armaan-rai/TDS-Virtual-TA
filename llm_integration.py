# llm_integration.py
from openai import OpenAI
import os
from typing import List, Dict

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_llm_answer(question: str, context_docs: List[Dict], model: str = "gpt-3.5-turbo") -> str:
    """Generate answer using LLM with context."""
    context = "\n\n".join([doc["content"] for doc in context_docs])
    
    prompt = f"""
    You are a teaching assistant for IIT Madras's Online Degree in Data Science program.
    Answer the student's question based on the provided context from course materials and discussions.
    
    Student Question: {question}
    
    Context:
    {context}
    
    Provide a concise, helpful answer. If the answer isn't in the context, say "I couldn't find a definitive answer in the course materials, but generally..." and provide a helpful response.
    """
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful teaching assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content

# Update the generate_answer function in main.py to use this