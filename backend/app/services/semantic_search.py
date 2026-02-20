"""Semantic Code Search Service using sentence-transformers"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Heavy imports (numpy, sentence-transformers/PyTorch) are deferred to
# SemanticSearchService.__init__ so that module import is instant.
np = None  # populated lazily
SentenceTransformer = None  # populated lazily


class SemanticSearchService:
    """Service for semantic code search using local embeddings (no API costs)"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize semantic search service.
        
        Args:
            model_name: Sentence transformer model to use.
                        all-MiniLM-L6-v2 is lightweight (80MB), fast, and produces 384-dim embeddings.
        """
        global np, SentenceTransformer

        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2

        # Attempt heavy imports only on first instantiation
        try:
            import numpy as _np
            from sentence_transformers import SentenceTransformer as _ST
            np = _np
            SentenceTransformer = _ST
        except ImportError:
            logger.debug("Semantic search disabled - sentence-transformers/numpy not installed")
            return

        try:
            # Load model (downloads ~80MB on first run, then cached locally)
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if semantic search is available"""
        return self.model is not None
    
    def embed_code(self, code: str, context: Optional[str] = None) -> Optional[np.ndarray]:
        """Generate embedding vector for code snippet.
        
        Args:
            code: Source code to embed
            context: Optional context (file path, function name, etc.)
        
        Returns:
            Numpy array of embedding vector, or None if unavailable
        """
        if not self.is_available():
            return None
        
        try:
            # Combine code with context for better embeddings
            if context:
                text = f"{context}\n\n{code}"
            else:
                text = code
            
            # Truncate if too long (models have token limits)
            max_chars = 8000  # ~2000 tokens
            if len(text) > max_chars:
                text = text[:max_chars]
            
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Code embedding failed: {e}")
            return None
    
    def embed_batch(self, texts: List[str]) -> Optional[np.ndarray]:
        """Embed multiple texts in a batch (faster than one-by-one).
        
        Args:
            texts: List of text strings to embed
        
        Returns:
            Numpy array of shape (n_texts, embedding_dim), or None
        """
        if not self.is_available():
            return None
        
        try:
            # Truncate each text
            max_chars = 8000
            truncated = [t[:max_chars] for t in texts]
            
            embeddings = self.model.encode(truncated, convert_to_numpy=True, show_progress_bar=False)
            return embeddings
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            return None
    
    def find_similar_code(
        self,
        query_code: str,
        code_database: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar code snippets using cosine similarity.
        
        Args:
            query_code: Code snippet to search for
            code_database: List of dicts with 'code' and 'embedding' keys
            top_k: Number of similar results to return
        
        Returns:
            List of code snippets with similarity scores, sorted by relevance
        """
        if not self.is_available():
            return []
        
        try:
            # Embed query
            query_embedding = self.embed_code(query_code)
            if query_embedding is None:
                return []
            
            # Calculate similarities
            results = []
            for item in code_database:
                if "embedding" not in item or item["embedding"] is None:
                    continue
                
                similarity = self._cosine_similarity(query_embedding, item["embedding"])
                results.append({
                    **item,
                    "similarity": float(similarity)
                })
            
            # Sort by similarity and return top_k
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:top_k]
        
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def search_similar_findings(
        self,
        db_session,
        query_description: str,
        project_id: Optional[int] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar findings across historical PR reviews.
        
        This helps identify patterns:
        - "We've seen this bug before in other files"
        - "This finding is similar to one we fixed last month"
        - "Other developers made the same mistake"
        
        Args:
            db_session: Database session
            query_description: Finding description to search for
            project_id: Optional filter by project
            top_k: Number of similar findings to return
        
        Returns:
            List of similar historical findings with metadata
        """
        if not self.is_available():
            return []
        
        try:
            from app.models import Finding
            
            # Get query embedding
            query_embedding = self.embed_code(query_description)
            if query_embedding is None:
                return []
            
            # Query database for findings with embeddings
            query = db_session.query(Finding).filter(Finding.embedding.isnot(None))
            if project_id:
                query = query.join(Finding.run).filter(Finding.run.has(project_id=project_id))
            
            findings = query.limit(1000).all()  # Limit to prevent memory issues
            
            # Calculate similarities
            results = []
            for finding in findings:
                if finding.embedding is None:
                    continue
                
                # Convert stored embedding back to numpy array
                embedding = np.array(finding.embedding)
                similarity = self._cosine_similarity(query_embedding, embedding)
                
                results.append({
                    "finding_id": finding.id,
                    "title": finding.title,
                    "description": finding.description,
                    "file_path": finding.file_path,
                    "severity": finding.severity.value,
                    "category": finding.category.value,
                    "similarity": float(similarity),
                    "run_id": finding.run_id
                })
            
            # Sort and return top results
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:top_k]
        
        except Exception as e:
            logger.error(f"Finding search failed: {e}")
            return []
    
    def analyze_finding_patterns(
        self,
        db_session,
        project_id: int,
        min_similarity: float = 0.75
    ) -> Dict[str, Any]:
        """Analyze recurring patterns in findings for a project.
        
        Returns:
            Dict with:
            - recurring_issues: List of issue patterns that keep appearing
            - hotspot_files: Files with repeated similar issues
            - learning_opportunities: Suggestions based on patterns
        """
        if not self.is_available():
            return {"recurring_issues": [], "hotspot_files": [], "learning_opportunities": []}
        
        try:
            from app.models import Finding, AnalysisRun
            from collections import defaultdict
            
            # Get all findings for project
            findings = (
                db_session.query(Finding)
                .join(AnalysisRun)
                .filter(AnalysisRun.project_id == project_id)
                .filter(Finding.embedding.isnot(None))
                .all()
            )
            
            if len(findings) < 5:
                return {"recurring_issues": [], "hotspot_files": [], "learning_opportunities": []}
            
            # Find clusters of similar findings
            clusters = defaultdict(list)
            processed = set()
            
            for i, finding1 in enumerate(findings):
                if i in processed:
                    continue
                
                cluster = [finding1]
                emb1 = np.array(finding1.embedding)
                
                for j, finding2 in enumerate(findings[i+1:], start=i+1):
                    if j in processed:
                        continue
                    
                    emb2 = np.array(finding2.embedding)
                    similarity = self._cosine_similarity(emb1, emb2)
                    
                    if similarity >= min_similarity:
                        cluster.append(finding2)
                        processed.add(j)
                
                if len(cluster) > 1:
                    clusters[finding1.title].extend(cluster)
            
            # Analyze clusters
            recurring_issues = []
            for title, cluster_findings in clusters.items():
                if len(cluster_findings) >= 2:
                    files = list(set(f.file_path for f in cluster_findings))
                    recurring_issues.append({
                        "issue_type": title,
                        "occurrences": len(cluster_findings),
                        "affected_files": files,
                        "example": cluster_findings[0].description[:200]
                    })
            
            # Find hotspot files
            file_issue_counts = defaultdict(int)
            for findings_list in clusters.values():
                for finding in findings_list:
                    file_issue_counts[finding.file_path] += 1
            
            hotspot_files = [
                {"file": file, "issue_count": count}
                for file, count in sorted(file_issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            
            # Generate learning opportunities
            learning_opportunities = []
            if recurring_issues:
                learning_opportunities.append(
                    f"Consider adding custom linting rules for the {len(recurring_issues)} recurring issue patterns detected."
                )
            if hotspot_files:
                top_hotspot = hotspot_files[0]
                learning_opportunities.append(
                    f"File '{top_hotspot['file']}' has {top_hotspot['issue_count']} recurring issues - consider refactoring."
                )
            
            return {
                "recurring_issues": recurring_issues,
                "hotspot_files": hotspot_files,
                "learning_opportunities": learning_opportunities
            }
        
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return {"recurring_issues": [], "hotspot_files": [], "learning_opportunities": []}


# Singleton instance
_semantic_search_service = None

def get_semantic_search_service() -> SemanticSearchService:
    """Get or create the semantic search service singleton"""
    global _semantic_search_service
    if _semantic_search_service is None:
        _semantic_search_service = SemanticSearchService()
    return _semantic_search_service
