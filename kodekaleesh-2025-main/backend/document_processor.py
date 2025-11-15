import json
import os
from datetime import datetime
import uuid
from typing import Dict, List, Any

class DocumentProcessor:
    """Handle document processing and storage"""
    
    def __init__(self):
        self.storage_file = 'documents.json'
        self.documents = self._load_documents()
    
    def _load_documents(self) -> Dict:
        """Load documents from JSON storage"""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_documents(self):
        """Save documents to JSON storage"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.documents, f, indent=2)
    
    def process(self, filepath: str, filename: str) -> Dict[str, Any]:
        """Process and store a document"""
        doc_id = str(uuid.uuid4())[:8]
        
        # Read document content
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            # Fallback for binary files
            with open(filepath, 'rb') as f:
                content = f.read().decode('utf-8', errors='ignore')
        
        # Extract basic metadata
        doc_data = {
            'id': doc_id,
            'filename': filename,
            'content': content,
            'created_at': datetime.now().isoformat(),
            'pages': max(1, len(content) // 3000),  # Rough estimate
            'text_length': len(content),
            'file_path': filepath
        }
        
        self.documents[doc_id] = doc_data
        self._save_documents()
        
        return doc_data
    
    def process_ocr_result(self, filepath: str, filename: str, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process and store OCR extraction result"""
        doc_id = str(uuid.uuid4())[:8]
        
        # Use OCR extracted text
        content = ocr_result.get('text', '')
        confidence = ocr_result.get('confidence', 0)
        
        # Extract basic metadata
        doc_data = {
            'id': doc_id,
            'filename': filename,
            'content': content,
            'created_at': datetime.now().isoformat(),
            'pages': max(1, len(content) // 3000),  # Rough estimate
            'text_length': len(content),
            'file_path': filepath,
            'source_type': 'ocr_image',
            'ocr_confidence': confidence
        }
        
        self.documents[doc_id] = doc_data
        self._save_documents()
        
        return doc_data
    
    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Retrieve a document"""
        return self.documents.get(doc_id)
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents"""
        return [
            {
                'id': doc['id'],
                'filename': doc['filename'],
                'created_at': doc['created_at'],
                'text_length': doc['text_length'],
                'pages': doc['pages']
            }
            for doc in self.documents.values()
        ]
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document"""
        if doc_id in self.documents:
            file_path = self.documents[doc_id].get('file_path')
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            del self.documents[doc_id]
            self._save_documents()
            return True
        return False
    
    def extract_metadata(self, doc_id: str) -> Dict[str, Any]:
        """Extract metadata from document"""
        doc = self.get_document(doc_id)
        if not doc:
            return {}
        
        content = doc['content']
        
        # Simple keyword extraction
        keywords = self._extract_keywords(content)
        
        return {
            'word_count': len(content.split()),
            'character_count': len(content),
            'keywords': keywords,
            'entities': self._extract_entities(content)
        }
    
    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract top keywords from text"""
        words = text.lower().split()
        # Filter common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        
        filtered = [w.strip('.,;:!?"\'') for w in words if w.lower() not in stop_words and len(w) > 3]
        
        # Count frequency
        from collections import Counter
        freq = Counter(filtered)
        
        return [word for word, _ in freq.most_common(top_n)]
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        entities = {
            'potential_case_names': [],
            'potential_dates': [],
            'potential_sections': []
        }
        
        # Simple pattern matching (basic)
        import re
        
        # Look for "Case v. Case" pattern
        case_pattern = r'(\w+\s+(?:v\.|versus)\s+\w+)'
        entities['potential_case_names'] = re.findall(case_pattern, text, re.IGNORECASE)[:5]
        
        # Look for dates
        date_pattern = r'\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{4}-\d{1,2}-\d{1,2}\b'
        entities['potential_dates'] = re.findall(date_pattern, text)[:5]
        
        # Look for section references
        section_pattern = r'(?:Section|§)\s+[\d\w\.\-]+'
        entities['potential_sections'] = re.findall(section_pattern, text, re.IGNORECASE)[:5]
        
        return entities
    
    def analyze(self, doc_ids: List[str], analysis_type: str = 'general') -> Dict[str, Any]:
        """Analyze documents"""
        insights = {
            'total_documents': len(doc_ids),
            'combined_word_count': 0,
            'key_themes': [],
            'document_summary': []
        }
        
        all_keywords = []
        
        for doc_id in doc_ids:
            doc = self.get_document(doc_id)
            if doc:
                insights['combined_word_count'] += len(doc['content'].split())
                metadata = self.extract_metadata(doc_id)
                all_keywords.extend(metadata.get('keywords', []))
                insights['document_summary'].append({
                    'id': doc_id,
                    'filename': doc['filename'],
                    'word_count': metadata['word_count']
                })
        
        # Get top themes
        from collections import Counter
        if all_keywords:
            theme_freq = Counter(all_keywords)
            insights['key_themes'] = [word for word, _ in theme_freq.most_common(5)]
        
        return insights
