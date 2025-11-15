from typing import Optional

class DocumentSummarizer:
    """Summarize legal documents"""
    
    def __init__(self):
        pass
    
    def summarize(self, text: str, max_length: int = 500) -> str:
        """Generate a summary of document text"""
        if len(text) <= max_length:
            return text
        
        # Simple extractive summarization
        sentences = self._split_sentences(text)
        
        # Score sentences based on keyword frequency
        scores = self._score_sentences(sentences, text)
        
        # Select top sentences
        top_sentences = sorted(
            enumerate(sentences),
            key=lambda x: scores.get(x[0], 0),
            reverse=True
        )[:3]
        
        # Sort by original order
        summary_sentences = sorted(top_sentences, key=lambda x: x[0])
        summary = ' '.join([s[1] for s in summary_sentences])
        
        # Trim to max length
        if len(summary) > max_length:
            summary = summary[:max_length] + '...'
        
        return summary
    
    def _split_sentences(self, text: str) -> list:
        """Split text into sentences"""
        import re
        # Simple sentence splitter
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _score_sentences(self, sentences: list, text: str) -> dict:
        """Score sentences based on keyword frequency"""
        # Get important words
        words = text.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        
        important_words = set(w.strip('.,;:!?"\'') for w in words if w.lower() not in stop_words and len(w) > 3)
        
        scores = {}
        for i, sentence in enumerate(sentences):
            score = sum(1 for word in important_words if word in sentence.lower())
            scores[i] = score
        
        return scores
    
    def extract_key_points(self, text: str, num_points: int = 5) -> list:
        """Extract key points from document"""
        sentences = self._split_sentences(text)
        scores = self._score_sentences(sentences, text)
        
        top_sentences = sorted(
            enumerate(sentences),
            key=lambda x: scores.get(x[0], 0),
            reverse=True
        )[:num_points]
        
        return [s[1] for s in sorted(top_sentences, key=lambda x: x[0])]
