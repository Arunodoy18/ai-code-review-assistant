from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AnalysisRun, Finding, Project, RunStatus
from app.config import settings
from app.tasks.analysis import analyze_pr_task
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/runs")
async def list_analysis_runs(
    project_id: Optional[int] = Query(None),
    pr_number: Optional[int] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """List analysis runs with optional filters. Guaranteed to never throw."""
    try:
        query = db.query(AnalysisRun)
        
        if project_id:
            query = query.filter(AnalysisRun.project_id == project_id)
        if pr_number:
            query = query.filter(AnalysisRun.pr_number == pr_number)
        
        query = query.order_by(AnalysisRun.started_at.desc())
        total = query.count()
        runs = query.offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "count": total,
            "data": runs
        }
    except Exception as e:
        logger.error(f"Error fetching analysis runs: {e}", exc_info=True)
        return {
            "success": False,
            "count": 0,
            "data": [],
            "error": str(e) if settings.environment == "development" else "Internal server error"
        }


@router.get("/runs/{run_id}")
async def get_analysis_run(run_id: int, db: Session = Depends(get_db)):
    """Get analysis run details"""
    run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/runs/{run_id}/findings")
async def get_run_findings(
    run_id: int,
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get findings for a specific run"""
    query = db.query(Finding).filter(Finding.run_id == run_id)
    
    if severity:
        query = query.filter(Finding.severity == severity)
    if category:
        query = query.filter(Finding.category == category)
    
    findings = query.all()
    
    # Group findings by file
    findings_by_file = {}
    for finding in findings:
        if finding.file_path not in findings_by_file:
            findings_by_file[finding.file_path] = []
        findings_by_file[finding.file_path].append(finding)
    
    return {
        "run_id": run_id,
        "total_findings": len(findings),
        "findings": findings,
        "findings_by_file": findings_by_file
    }


@router.post("/runs/{run_id}/rerun")
async def rerun_analysis(run_id: int, db: Session = Depends(get_db)):
    """Trigger a re-run of analysis for failed or completed runs"""
    run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    # Check if run can be rerun (only allow failed or completed runs to be rerun)
    if run.status not in [RunStatus.FAILED, RunStatus.COMPLETED]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot rerun analysis with status: {run.status}. Only failed or completed runs can be rerun."
        )
    
    if not settings.enable_background_tasks:
        raise HTTPException(status_code=503, detail="Background tasks are disabled in this environment")

    # Delete existing findings
    db.query(Finding).filter(Finding.run_id == run_id).delete()
    
    # Reset run status and timestamps
    run.status = RunStatus.PENDING
    run.started_at = datetime.utcnow()
    run.completed_at = None
    run.error_message = None
    run.run_metadata = {}
    db.commit()

    # Trigger celery task for analysis
    try:
        analyze_pr_task.delay(run_id)
        return {
            "message": "Re-run triggered successfully",
            "run_id": run_id,
            "status": "pending"
        }
    except Exception as e:
        run.status = RunStatus.FAILED
        run.error_message = f"Failed to queue re-run: {str(e)}"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/findings/{finding_id}/resolve")
async def resolve_finding(finding_id: int, db: Session = Depends(get_db)):
    """Mark a finding as resolved"""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    finding.is_resolved = 1
    db.commit()
    
    return {"message": "Finding resolved", "finding_id": finding_id}


@router.patch("/findings/{finding_id}/dismiss")
async def dismiss_finding(finding_id: int, db: Session = Depends(get_db)):
    """Dismiss a finding and learn from it (false-positive suppression).
    
    This marks the finding as dismissed and records the pattern so
    similar findings can be auto-suppressed in future runs.
    """
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    finding.is_dismissed = 1
    
    # Learn: record the dismissed pattern on the project
    run = db.query(AnalysisRun).filter(AnalysisRun.id == finding.run_id).first()
    if run:
        project = db.query(Project).filter(Project.id == run.project_id).first()
        if project:
            patterns = project.dismissed_patterns or []
            pattern = {
                "rule_id": finding.rule_id,
                "title": finding.title,
                "file_pattern": finding.file_path.rsplit("/", 1)[-1] if "/" in finding.file_path else finding.file_path,
                "category": finding.category.value if hasattr(finding.category, 'value') else str(finding.category),
                "dismissed_count": 1,
            }
            # Check if pattern already exists
            existing = next((p for p in patterns if p.get("rule_id") == pattern["rule_id"] and p.get("title") == pattern["title"]), None)
            if existing:
                existing["dismissed_count"] = existing.get("dismissed_count", 0) + 1
            else:
                patterns.append(pattern)
            project.dismissed_patterns = patterns
    
    db.commit()
    
    return {"message": "Finding dismissed and pattern learned", "finding_id": finding_id}


@router.get("/findings/{finding_id}/auto-fix")
async def get_auto_fix(finding_id: int, db: Session = Depends(get_db)):
    """Get the AI-generated auto-fix for a finding"""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    return {
        "finding_id": finding_id,
        "has_fix": bool(finding.auto_fix_code),
        "auto_fix_code": finding.auto_fix_code,
    }


@router.post("/findings/{finding_id}/generate-fix")
async def generate_fix_on_demand(finding_id: int, db: Session = Depends(get_db)):
    """Generate an auto-fix on demand for a finding that doesn't have one yet"""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    if finding.auto_fix_code:
        return {"finding_id": finding_id, "auto_fix_code": finding.auto_fix_code, "cached": True}
    
    try:
        from app.services.llm_service import LLMService
        llm = LLMService()
        
        finding_data = {
            "title": finding.title,
            "severity": finding.severity.value if hasattr(finding.severity, 'value') else str(finding.severity),
            "file_path": finding.file_path,
            "line_number": finding.line_number,
            "description": finding.description,
            "suggestion": finding.suggestion,
        }
        
        fix = llm.generate_auto_fix(finding_data, finding.code_snippet or "")
        if fix:
            finding.auto_fix_code = fix
            db.commit()
        
        return {"finding_id": finding_id, "auto_fix_code": fix, "cached": False}
    except Exception as e:
        logger.error(f"On-demand fix generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate fix")


@router.get("/runs/{run_id}/risk-score")
async def get_risk_score(run_id: int, db: Session = Depends(get_db)):
    """Get the PR risk score for an analysis run"""
    run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return {
        "run_id": run_id,
        "risk_score": run.risk_score,
        "risk_breakdown": run.risk_breakdown or {},
    }


@router.get("/runs/{run_id}/summary")
async def get_pr_summary(run_id: int, db: Session = Depends(get_db)):
    """Get the natural language PR summary for non-technical stakeholders"""
    run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return {
        "run_id": run_id,
        "pr_summary": run.pr_summary,
        "has_summary": bool(run.pr_summary),
    }


@router.get("/runs/{run_id}/dismissed")
async def get_dismissed_findings(run_id: int, db: Session = Depends(get_db)):
    """Get findings that were dismissed in this run"""
    findings = db.query(Finding).filter(Finding.run_id == run_id, Finding.is_dismissed == 1).all()
    return {
        "run_id": run_id,
        "dismissed_count": len(findings),
        "findings": findings,
    }
