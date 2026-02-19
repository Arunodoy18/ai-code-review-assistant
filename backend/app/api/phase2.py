"""API endpoints for Phase 2 features: Semantic Search and Pattern Analysis"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Project
from app.services.semantic_search import get_semantic_search_service
from app.services.code_sandbox import get_code_sandbox
from app.api.auth import get_current_user
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class SimilarFindingsRequest(BaseModel):
    """Request to search for similar historical findings"""
    query: str
    project_id: Optional[int] = None
    top_k: int = 5


class PatternAnalysisRequest(BaseModel):
    """Request for pattern analysis"""
    project_id: int
    min_similarity: float = 0.75


class SandboxTestRequest(BaseModel):
    """Request to test code in sandbox"""
    code: str
    language: str = "python"
    test_code: Optional[str] = None


class AutoFixTestRequest(BaseModel):
    """Request to test an auto-fix"""
    original_code: str
    fixed_code: str
    language: str = "python"
    test_cases: Optional[str] = None


@router.post("/search/similar-findings")
async def search_similar_findings(
    request: SimilarFindingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for similar findings across historical PR reviews.
    
    This helps identify patterns like:
    - "We've seen this bug before in other files"
    - "This finding is similar to one we fixed last month"
    - "Other developers made the same mistake"
    """
    semantic_search = get_semantic_search_service()
    
    if not semantic_search.is_available():
        raise HTTPException(
            status_code=503,
            detail="Semantic search not available. sentence-transformers may not be installed."
        )
    
    # Verify project access if specified
    if request.project_id:
        project = db.query(Project).filter(
            Project.id == request.project_id,
            Project.owner_id == current_user.id
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    
    # Search for similar findings
    try:
        similar_findings = semantic_search.search_similar_findings(
            db,
            query_description=request.query,
            project_id=request.project_id,
            top_k=request.top_k
        )
        
        return {
            "query": request.query,
            "similar_findings": similar_findings,
            "count": len(similar_findings)
        }
    except Exception as e:
        logger.error(f"Similar findings search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analysis/patterns")
async def analyze_patterns(
    request: PatternAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze recurring patterns in findings for a project.
    
    Returns:
    - recurring_issues: List of issue patterns that keep appearing
    - hotspot_files: Files with repeated similar issues
    - learning_opportunities: Suggestions based on patterns
    """
    semantic_search = get_semantic_search_service()
    
    if not semantic_search.is_available():
        raise HTTPException(
            status_code=503,
            detail="Semantic search not available"
        )
    
    # Verify project access
    project = db.query(Project).filter(
        Project.id == request.project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Analyze patterns
    try:
        patterns = semantic_search.analyze_finding_patterns(
            db,
            project_id=request.project_id,
            min_similarity=request.min_similarity
        )
        
        return {
            "project_id": request.project_id,
            "project_name": project.name,
            **patterns
        }
    except Exception as e:
        logger.error(f"Pattern analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sandbox/test")
async def test_code_sandbox(
    request: SandboxTestRequest,
    current_user: User = Depends(get_current_user)
):
    """Test code execution in a sandboxed environment.
    
    Useful for:
    - Verifying auto-fixes don't break code
    - Testing code snippets before suggesting them
    - Running security checks
    """
    sandbox = get_code_sandbox()
    
    if not sandbox.is_available():
        raise HTTPException(
            status_code=503,
            detail="Code sandbox not available. Docker may not be running."
        )
    
    try:
        if request.language == "python":
            result = sandbox.test_python_code(
                request.code,
                request.test_code
            )
        elif request.language in ["javascript", "typescript"]:
            result = sandbox.test_javascript_code(
                request.code,
                request.test_code
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Language '{request.language}' not supported"
            )
        
        return {
            "language": request.language,
            **result
        }
    except Exception as e:
        logger.error(f"Sandbox test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sandbox/test-auto-fix")
async def test_auto_fix(
    request: AutoFixTestRequest,
    current_user: User = Depends(get_current_user)
):
    """Test if an auto-fix actually works without breaking code.
    
    Compares execution results of original vs fixed code to verify:
    - Fix doesn't introduce new errors
    - Fix resolves the original issue
    - Fix maintains expected behavior
    """
    sandbox = get_code_sandbox()
    
    if not sandbox.is_available():
        raise HTTPException(
            status_code=503,
            detail="Code sandbox not available. Docker may not be running."
        )
    
    try:
        result = sandbox.test_auto_fix(
            original_code=request.original_code,
            fixed_code=request.fixed_code,
            language=request.language,
            test_cases=request.test_cases
        )
        
        return {
            "language": request.language,
            **result
        }
    except Exception as e:
        logger.error(f"Auto-fix test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sandbox/status")
async def sandbox_status(
    current_user: User = Depends(get_current_user)
):
    """Check if sandbox and semantic search services are available"""
    sandbox = get_code_sandbox()
    semantic_search = get_semantic_search_service()
    
    return {
        "sandbox": {
            "available": sandbox.is_available(),
            "status": "ready" if sandbox.is_available() else "unavailable"
        },
        "semantic_search": {
            "available": semantic_search.is_available(),
            "status": "ready" if semantic_search.is_available() else "unavailable",
            "embedding_dim": semantic_search.embedding_dim if semantic_search.is_available() else None
        },
        "phase2_enabled": sandbox.is_available() or semantic_search.is_available()
    }
