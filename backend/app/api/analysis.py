from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AnalysisRun, Finding, Project, RunStatus
from app.tasks.analysis import analyze_pr_task
from typing import Optional, List
from datetime import datetime

router = APIRouter()


@router.get("/runs")
async def list_analysis_runs(
    project_id: Optional[int] = Query(None),
    pr_number: Optional[int] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """List analysis runs with optional filters"""
    query = db.query(AnalysisRun)
    
    if project_id:
        query = query.filter(AnalysisRun.project_id == project_id)
    if pr_number:
        query = query.filter(AnalysisRun.pr_number == pr_number)
    
    query = query.order_by(AnalysisRun.started_at.desc())
    total = query.count()
    runs = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "runs": runs
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
