import re
from collections import defaultdict
from difflib import SequenceMatcher
from typing import List, Optional, Dict, Tuple

class HotWordDetector:
    def __init__(self, sensitivity=0.75):
        """
        Initialize the hotword detector with a sensitivity threshold
        
        Args:
            sensitivity (float): Matching threshold (0-1), higher values require more exact matches
        """
        self.sensitivity = sensitivity
        self.word_groups = defaultdict(list)
        self.patterns = {}
        self.hotwords = {}
        
    def add_hotword(self, name: str, variations: List[str]):
        """
        Register a new hotword with its variations
        
        Args:
            name (str): Identifier for the hotword
            variations (List[str]): List of phrase variations that should trigger this hotword
        """
        self.hotwords[name] = variations
        pattern = r'\b(?:' + '|'.join(map(re.escape, variations)) + r')\b'
        self.patterns[name] = re.compile(pattern, re.IGNORECASE)
        
    def add_word_group(self, group_name: str, words: List[str]):
        """
        Add a group of related words for detection
        
        Args:
            group_name (str): Name for this word group
            words (List[str]): List of words in this group
        """
        self.word_groups[group_name] = words
        pattern = r'\b(?:' + '|'.join(map(re.escape, words)) + r')\b'
        self.patterns[group_name] = re.compile(pattern, re.IGNORECASE)
        
    def detect(self, text: str, name: str) -> bool:
        """
        Check if a specific hotword or word group appears in the text
        
        Args:
            text (str): Input text to analyze
            name (str): Name of the hotword or word group to check
            
        Returns:
            bool: True if detected, False otherwise
        """
        if name not in self.patterns:
            return False
        return bool(self.patterns[name].search(text.lower()))
        
    def detect_any(self, text: str) -> Optional[str]:
        """
        Detect any registered hotword in the text
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Optional[str]: Name of the detected hotword or None if none found
        """
        text_lower = text.lower()
        for name, variations in self.hotwords.items():
            if any(variation in text_lower for variation in variations):
                return name
        return None
        
    def detect_similar(self, text: str, target: str, threshold=None) -> bool:
        """
        Fuzzy matching detection for similar words
        
        Args:
            text (str): Input text to analyze
            target (str): Target word to match against
            threshold (float, optional): Custom similarity threshold
            
        Returns:
            bool: True if similar word found
        """
        threshold = threshold or self.sensitivity
        words = text.lower().split()
        target = target.lower()
        
        for word in words:
            similarity = SequenceMatcher(None, word, target).ratio()
            if similarity >= threshold:
                return True
        return False
        
    def extract_matches(self, text: str, name: str) -> List[str]:
        """
        Extract all matching words from text for a specific hotword or group
        
        Args:
            text (str): Input text to analyze
            name (str): Name of the hotword or word group
            
        Returns:
            List[str]: List of matched words/phrases
        """
        if name not in self.patterns:
            return []
        return self.patterns[name].findall(text.lower())
        
    def get_most_similar(self, text: str, name: str) -> Optional[str]:
        """
        Find the most similar word from a group in the text
        
        Args:
            text (str): Input text to analyze
            name (str): Name of the word group
            
        Returns:
            Optional[str]: Best matching word or None
        """
        if name not in self.word_groups:
            return None
            
        text_words = text.lower().split()
        best_match = None
        highest_score = 0
        
        for target in self.word_groups[name]:
            for word in text_words:
                score = SequenceMatcher(None, word, target.lower()).ratio()
                if score > highest_score and score >= self.sensitivity:
                    highest_score = score
                    best_match = target
                    
        return best_match
        
    def remove_hotword(self, name: str):
        """
        Remove a registered hotword
        
        Args:
            name (str): Name of the hotword to remove
        """
        if name in self.hotwords:
            del self.hotwords[name]
            del self.patterns[name]
            
    def clear_hotwords(self):
        """Clear all registered hotwords"""
        self.hotwords.clear()
        self.patterns.clear()