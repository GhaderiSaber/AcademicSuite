#!/usr/bin/env python3
"""
Word Document Comment Extractor (extract_docx_comments.py)
---------------------------------------------------------
Extracts margin comments, authors, timestamps, and highlighted text passages
from Microsoft Word (.docx) documents using OpenXML inspection.
Also supports importing raw text/markdown feedback lists from emails or defense meetings.

Output:
A structured JSON file (comments.json) ready for revision planning and response table generation.
"""

import os
import sys
import json
import zipfile
import argparse
import xml.etree.ElementTree as ET

# Word OpenXML Namespaces
NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml'
}

def extract_comments_from_docx(docx_path: str) -> list:
    """Extract comments and their anchored text from a .docx file."""
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"Document not found: {docx_path}")
        
    comments = []
    
    with zipfile.ZipFile(docx_path, 'r') as z:
        # Check if word/comments.xml exists
        if 'word/comments.xml' not in z.namelist():
            print(f"No comments found in {docx_path} (word/comments.xml does not exist).")
            return []
            
        comments_xml = z.read('word/comments.xml')
        root_comments = ET.fromstring(comments_xml)
        
        # Read document.xml to map commentRangeStart/End
        doc_xml = z.read('word/document.xml')
        root_doc = ET.fromstring(doc_xml)
        
        # Build map of comment ID -> selected text
        comment_ranges = {}
        
        # Walk document paragraphs and runs to find commentRangeStart/End
        current_comment_id = None
        for elem in root_doc.iter():
            tag = elem.tag.split('}')[-1]
            if tag == 'commentRangeStart':
                c_id = elem.get(f"{{{NS['w']}}}id")
                comment_ranges[c_id] = []
                current_comment_id = c_id
            elif tag == 'commentRangeEnd':
                current_comment_id = None
            elif tag == 't' and current_comment_id:
                if elem.text:
                    comment_ranges[current_comment_id].append(elem.text)
                    
        # Parse comments.xml
        for c in root_comments.findall('.//w:comment', NS):
            c_id = c.get(f"{{{NS['w']}}}id")
            author = c.get(f"{{{NS['w']}}}author", "استاد راهنما")
            date = c.get(f"{{{NS['w']}}}date", "")
            
            # Extract text of the comment
            comment_paragraphs = []
            for p in c.findall('.//w:p', NS):
                texts = [t.text for t in p.findall('.//w:t', NS) if t.text]
                if texts:
                    comment_paragraphs.append("".join(texts))
            comment_text = " ".join(comment_paragraphs).strip()
            
            # Selected text from range
            selected_words = comment_ranges.get(c_id, [])
            selected_text = "".join(selected_words).strip() if selected_words else ""
            
            comments.append({
                "id": int(c_id) if c_id.isdigit() else c_id,
                "author": author,
                "date": date,
                "selected_text": selected_text,
                "comment": comment_text,
                "action_taken": "",
                "status": "pending",
                "location": ""
            })
            
    return comments

def parse_text_feedback(file_path: str) -> list:
    """Parse raw text/markdown bulleted feedback from email or defense minutes."""
    comments = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    c_id = 1
    for line in lines:
        line_str = line.strip()
        if not line_str or line_str.startswith('#'):
            continue
        # Strip leading bullet points or numbers (e.g., "1.", "-", "*")
        cleaned = line_str.lstrip('0123456789.-*• \t')
        if cleaned:
            comments.append({
                "id": c_id,
                "author": "استاد راهنما / داور",
                "date": "",
                "selected_text": "",
                "comment": cleaned,
                "action_taken": "",
                "status": "pending",
                "location": ""
            })
            c_id += 1
            
    return comments

def main():
    parser = argparse.ArgumentParser(description="Word & Text Comment Extractor for Academic Theses")
    parser.add_argument("--file", required=True, help="Path to reviewed .docx or text/markdown feedback file")
    parser.add_argument("--out", default="supervisor_comments.json", help="Output JSON file path")
    args = parser.parse_args()
    
    ext = os.path.splitext(args.file)[1].lower()
    if ext == '.docx':
        comments = extract_comments_from_docx(args.file)
    else:
        comments = parse_text_feedback(args.file)
        
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
        
    print(f"Extracted {len(comments)} comments. Output saved to: {args.out}")

if __name__ == "__main__":
    main()
