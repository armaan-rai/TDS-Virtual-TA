# data_processor.py
import re
from datetime import datetime
from typing import List, Dict
import json

def clean_text(text: str) -> str:
    """Clean and normalize the text content."""
    # Remove multiple whitespaces
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters except basic punctuation
    text = re.sub(r'[^\w\s.,!?\-]', '', text)
    return text.strip()

def process_content_file(input_file: str, output_file: str):
    """Process the scraped content file into structured data."""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by document separator
    documents = [doc.strip() for doc in content.split('---') if doc.strip()]
    
    processed_data = []
    for doc in documents:
        # Extract source URL if present
        source_match = re.search(r'\[Source\]\((.*?)\)', doc)
        source_url = source_match.group(1) if source_match else "Unknown"
        
        # Clean the content
        clean_doc = re.sub(r'\[Source\]\(.*?\)', '', doc)
        clean_doc = clean_text(clean_doc)
        
        # Extract date if possible
        date = extract_date_from_text(clean_doc) or extract_date_from_text(source_url)
        
        processed_data.append({
            "content": clean_doc,
            "source_url": source_url,
            "date": date.strftime('%Y-%m-%d') if date else None,
            "length": len(clean_doc)
        })
    
    # Save processed data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=2)
    
    print(f"Processed {len(processed_data)} documents saved to {output_file}")

def extract_date_from_text(text: str) -> datetime:
    """Extract date from text using multiple patterns."""
    date_patterns = [
        r'(\d{1,2}\s+\w+\s+\d{4})',  # 15 April 2025
        r'(\w+\s+\d{1,2},\s+\d{4})', # April 15, 2025
        r'(\d{4}-\d{2}-\d{2})'       # 2025-04-15
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            for fmt in ['%d %B %Y', '%B %d, %Y', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
    return None

# Run the processor
process_content_file("extracted_contents_filtered_v1.doc", "processed_data.json")