import json
import os
from typing import List, Dict, Any

class SearchEngine:
    """Search across documents"""
    
    def __init__(self):
        self.storage_file = 'documents.json'
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents for a query"""
        if not os.path.exists(self.storage_file):
            return []
        
        with open(self.storage_file, 'r') as f:
            documents = json.load(f)
        
        query_lower = query.lower()
        results = []
        
        for doc_id, doc_data in documents.items():
            content = doc_data.get('content', '').lower()
            filename = doc_data.get('filename', '').lower()
            
            # Calculate relevance score
            score = 0
            
            # Exact phrase match gets highest score
            if query_lower in content:
                score += 100
            
            # Word matches
            query_words = query_lower.split()
            for word in query_words:
                score += content.count(word) * 5
                if word in filename:
                    score += 20
            
            if score > 0:
                # Extract context snippets
                snippets = self._extract_snippets(doc_data['content'], query, max_snippets=2)
                
                results.append({
                    'document_id': doc_id,
                    'filename': doc_data['filename'],
                    'relevance_score': score,
                    'match_count': content.count(query_lower),
                    'snippets': snippets,
                    'created_at': doc_data['created_at']
                })
        
        # Sort by relevance score
        results = sorted(results, key=lambda x: x['relevance_score'], reverse=True)
        
        return results[:limit]
    
    def _extract_snippets(self, text: str, query: str, max_snippets: int = 2) -> List[str]:
        """Extract text snippets containing the query"""
        snippets = []
        query_lower = query.lower()
        text_lower = text.lower()
        
        start = 0
        snippet_count = 0
        
        while snippet_count < max_snippets:
            pos = text_lower.find(query_lower, start)
            if pos == -1:
                break
            
            # Extract surrounding context (50 chars before and after)
            snippet_start = max(0, pos - 50)
            snippet_end = min(len(text), pos + len(query) + 50)
            
            snippet = text[snippet_start:snippet_end].strip()
            if snippet_start > 0:
                snippet = '...' + snippet
            if snippet_end < len(text):
                snippet = snippet + '...'
            
            snippets.append(snippet)
            start = pos + len(query)
            snippet_count += 1
        
        return snippets
    
    def advanced_search(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Advanced search with filters"""
        if not os.path.exists(self.storage_file):
            return []
        
        with open(self.storage_file, 'r') as f:
            documents = json.load(f)
        
        results = []
        
        for doc_id, doc_data in documents.items():
            # Apply filters
            if filters.get('filename') and filters['filename'] not in doc_data.get('filename', ''):
                continue
            
            if filters.get('min_length') and doc_data.get('text_length', 0) < filters['min_length']:
                continue
            
            if filters.get('max_length') and doc_data.get('text_length', 0) > filters['max_length']:
                continue
            
            results.append({
                'id': doc_id,
                'filename': doc_data['filename'],
                'created_at': doc_data['created_at'],
                'text_length': doc_data['text_length']
            })
        
        return results
