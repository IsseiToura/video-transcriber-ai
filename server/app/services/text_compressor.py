"""
Text compression service using MMR algorithm with sentence-transformers.
"""

import re
import logging
from typing import Dict, List
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logger = logging.getLogger(__name__)


class TextCompressor:
    """Text compression class using preprocessing and MMR algorithm with embeddings."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with sentence transformer model."""
        self.model = SentenceTransformer(model_name)
        self.embeddings_cache = {}
        logger.info(f"TextCompressor initialized with model: {model_name}")
    
    def compress_segments(self, segments: List[Dict]) -> str:
        """Compress segments using text preprocessing, embeddings, and MMR."""
        logger.info(f"Starting text compression for {len(segments)} segments")
        
        # Extract text from segments
        segment_texts = []
        for segment in segments:
            if segment.get("text", "").strip():
                segment_texts.append(segment["text"].strip())
        
        if not segment_texts:
            logger.warning("No valid text segments found for compression")
            return ""
        
        logger.info(f"Extracted {len(segment_texts)} valid text segments")
        
        # Preprocess text (normalization, deduplication)
        processed_texts = self._preprocess_texts(segment_texts)
        logger.info(f"Text preprocessing completed. {len(processed_texts)} texts after preprocessing")
        
        if len(processed_texts) <= 3:  # If few segments, return as is
            logger.info("Few segments detected, returning all texts without compression")
            return " ".join(processed_texts)
        
        # Calculate optimal number of texts to select based on segment count
        optimal_num_select = self._calculate_optimal_num_select(len(processed_texts))
        logger.info(f"Calculated optimal selection: {optimal_num_select} texts from {len(processed_texts)}")
        
        # Use MMR to select representative sentences
        representative_texts = self._select_representative_texts(processed_texts, num_select=optimal_num_select)
        
        compressed_result = " ".join(representative_texts)
        logger.info(f"Text compression completed successfully. Original: {len(processed_texts)} texts, Compressed: {len(representative_texts)} texts")
        
        return compressed_result
    
    def _calculate_optimal_num_select(self, total_segments: int) -> int:
        """
        Calculate optimal number of segments to select based on total count.
        
        Args:
            total_segments: Total number of segments to select from
            
        Returns:
            Optimal number of segments to select
        """
        if total_segments <= 20:
            # Very few segments: select all
            return total_segments
        elif total_segments <= 50:
            # Small number: select about 30%
            return max(10, total_segments // 3)
        elif total_segments <= 100:
            # Medium number: select about 25%
            return max(15, total_segments // 4)
        elif total_segments <= 200:
            # Large number: select about 20%
            return max(20, total_segments // 5)
        else:
            # Very large number: select about 15-18%
            return max(30, total_segments // 6)
    
    def _preprocess_texts(self, texts: List[str]) -> List[str]:
        """Preprocess texts: normalize, remove duplicates, clean up."""
        logger.debug(f"Starting text preprocessing for {len(texts)} texts")
        processed = []
        seen = set()
        
        for text in texts:
            # Normalize text
            normalized = self._normalize_text(text)
            
            # Remove duplicates
            if normalized not in seen and len(normalized.strip()) > 25:  # Updated for English
                processed.append(normalized)
                seen.add(normalized)
        
        logger.debug(f"Text preprocessing completed. {len(processed)} texts after deduplication")
        return processed
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text: remove extra whitespace, normalize punctuation."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize punctuation
        text = re.sub(r'[.!?]+', '.', text)
        
        # Ensure proper sentence ending
        if text and not text.endswith('.'):
            text += '.'
        
        return text
    
    def _select_representative_texts(self, texts: List[str], num_select: int = None, lambda_param: float = 0.5) -> List[str]:
        """
        Select representative texts using MMR (Maximal Marginal Relevance).
        
        Args:
            texts: List of texts to select from
            num_select: Number of texts to select (if None, calculated automatically)
            lambda_param: Balance between relevance (λ) and diversity (1-λ)
        """
        logger.debug(f"Starting MMR selection for {len(texts)} texts, target: {num_select}")
        
        if len(texts) <= 1:
            return texts
        
        # If num_select is not specified, calculate optimal number
        if num_select is None:
            num_select = self._calculate_optimal_num_select(len(texts))
        
        # Ensure num_select doesn't exceed available texts
        num_select = min(num_select, len(texts))
        
        if len(texts) <= num_select:
            logger.debug("All texts will be selected (no compression needed)")
            return texts
        
        # Get embeddings for all texts
        logger.debug("Generating embeddings for texts")
        embeddings = self._get_embeddings(texts)
        
        # Calculate similarity matrix
        logger.debug("Calculating cosine similarity matrix")
        similarity_matrix = cosine_similarity(embeddings)
        
        # Initialize selection
        selected_indices = []
        remaining_indices = list(range(len(texts)))
        
        # Select first text (highest average similarity to all others)
        avg_similarities = np.mean(similarity_matrix, axis=1)
        first_idx = np.argmax(avg_similarities)
        selected_indices.append(first_idx)
        remaining_indices.remove(first_idx)
        
        # Select remaining texts using MMR
        while len(selected_indices) < num_select and remaining_indices:
            mmr_scores = []
            
            for idx in remaining_indices:
                # Relevance: similarity to the query (using average similarity to all texts)
                relevance = avg_similarities[idx]
                
                # Diversity: minimum similarity to already selected texts
                if selected_indices:
                    diversity = 1 - np.max(similarity_matrix[idx, selected_indices])
                else:
                    diversity = 1
                
                # MMR score: λ * relevance + (1-λ) * diversity
                mmr_score = lambda_param * relevance + (1 - lambda_param) * diversity
                mmr_scores.append(mmr_score)
            
            # Select text with highest MMR score
            best_idx = remaining_indices[np.argmax(mmr_scores)]
            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)
        
        # Return selected texts
        selected_texts = [texts[i] for i in selected_indices]
        logger.debug(f"MMR selection completed. Selected {len(selected_texts)} representative texts")
        return selected_texts
    
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for texts using sentence-transformers."""
        logger.debug(f"Generating embeddings for {len(texts)} texts")
        embeddings = []
        cache_hits = 0
        
        for text in texts:
            if text in self.embeddings_cache:
                embeddings.append(self.embeddings_cache[text])
                cache_hits += 1
            else:
                embedding = self.model.encode(text, convert_to_tensor=False)
                self.embeddings_cache[text] = embedding
                embeddings.append(embedding)
        
        logger.debug(f"Embeddings generated. Cache hits: {cache_hits}/{len(texts)}")
        return np.array(embeddings)