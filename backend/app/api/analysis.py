from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AnalysisRun, Finding, Project, User, RunStatus
from app.config import settings
from app.services.auth_service import get_current_user
from app.tasks.analysis import analyze_pr_task
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()


class AnalyzePRRequest(BaseModel):
    project_id: int
    pr_number: int


@router.get("/runs")
async def list_analysis_runs(
    project_id: Optional[int] = Query(None),
    pr_number: Optional[int] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List analysis runs for projects owned by the authenticated user."""
    try:
        # Only show runs for projects owned by this user
        user_project_ids = [p.id for p in db.query(Project.id).filter(Project.owner_id == current_user.id).all()]
        query = db.query(AnalysisRun).filter(AnalysisRun.project_id.in_(user_project_ids))
        
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


def _verify_run_ownership(run_id: int, current_user: User, db: Session) -> AnalysisRun:
    """Verify that the analysis run belongs to a project owned by the current user."""
    run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    project = db.query(Project).filter(Project.id == run.project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


def _verify_finding_ownership(finding_id: int, current_user: User, db: Session) -> Finding:
    """Verify that the finding belongs to a project owned by the current user."""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    run = db.query(AnalysisRun).filter(AnalysisRun.id == finding.run_id).first()
    if run:
        project = db.query(Project).filter(Project.id == run.project_id, Project.owner_id == current_user.id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.get("/runs/{run_id}")
async def get_analysis_run(run_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get analysis run details (must belong to current user's project)"""
    return _verify_run_ownership(run_id, current_user, db)


@router.get("/runs/{run_id}/findings")
async def get_run_findings(
    run_id: int,
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get findings for a specific run (must belong to current user's project)"""
    _verify_run_ownership(run_id, current_user, db)
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
async def rerun_analysis(run_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Trigger a re-run of analysis for failed or completed runs"""
    run = _verify_run_ownership(run_id, current_user, db)
    
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
async def resolve_finding(finding_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Mark a finding as resolved"""
    finding = _verify_finding_ownership(finding_id, current_user, db)
    
    finding.is_resolved = 1
    db.commit()
    
    return {"message": "Finding resolved", "finding_id": finding_id}


@router.patch("/findings/{finding_id}/dismiss")
async def dismiss_finding(finding_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Dismiss a finding and learn from it (false-positive suppression).
    
    This marks the finding as dismissed and records the pattern so
    similar findings can be auto-suppressed in future runs.
    """
    finding = _verify_finding_ownership(finding_id, current_user, db)
    
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
async def get_auto_fix(finding_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get the AI-generated auto-fix for a finding"""
    finding = _verify_finding_ownership(finding_id, current_user, db)
    
    return {
        "finding_id": finding_id,
        "has_fix": bool(finding.auto_fix_code),
        "auto_fix_code": finding.auto_fix_code,
    }


@router.post("/findings/{finding_id}/generate-fix")
async def generate_fix_on_demand(finding_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Generate an auto-fix on demand for a finding that doesn't have one yet"""
    finding = _verify_finding_ownership(finding_id, current_user, db)
    
    if finding.auto_fix_code:
        return {"finding_id": finding_id, "auto_fix_code": finding.auto_fix_code, "cached": True}
    
    try:
        from app.services.llm_service import LLMService
        # Use per-user API keys if configured
        user_keys = {
            "groq_api_key": current_user.groq_api_key,
            "openai_api_key": current_user.openai_api_key,
            "anthropic_api_key": current_user.anthropic_api_key,
            "google_api_key": current_user.google_api_key,
            "preferred_llm_provider": current_user.preferred_llm_provider,
        }
        llm = LLMService(user_keys=user_keys)
        
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
async def get_risk_score(run_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get the PR risk score for an analysis run"""
    run = _verify_run_ownership(run_id, current_user, db)
    
    return {
        "run_id": run_id,
        "risk_score": run.risk_score,
        "risk_breakdown": run.risk_breakdown or {},
    }


@router.get("/runs/{run_id}/summary")
async def get_pr_summary(run_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get the natural language PR summary for non-technical stakeholders"""
    run = _verify_run_ownership(run_id, current_user, db)
    
    return {
        "run_id": run_id,
        "pr_summary": run.pr_summary,
        "has_summary": bool(run.pr_summary),
    }


@router.get("/runs/{run_id}/dismissed")
async def get_dismissed_findings(run_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get findings that were dismissed in this run"""
    _verify_run_ownership(run_id, current_user, db)
    findings = db.query(Finding).filter(Finding.run_id == run_id, Finding.is_dismissed == 1).all()
    return {
        "run_id": run_id,
        "dismissed_count": len(findings),
        "findings": findings,
    }


@router.post("/analyze-pr")
async def analyze_pr_manual(
    body: AnalyzePRRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually trigger PR analysis via the user's GitHub PAT.
    Fetches PR info, creates an AnalysisRun, and runs analysis inline (synchronous)
    or queues it via Celery if background tasks are enabled.
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == body.project_id,
        Project.owner_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Phase 3B: Check usage limits
    from app.services.usage_service import UsageService
    
    can_analyze, error_msg = UsageService.can_perform_analysis(current_user, db)
    if not can_analyze:
        raise HTTPException(status_code=403, detail=error_msg)

    # Check GitHub token
    if not current_user.github_token:
        raise HTTPException(
            status_code=400,
            detail="Please configure your GitHub Personal Access Token in Settings first.",
        )

    # Fetch PR info via PAT
    from app.services.github_pat_service import GitHubPATService

    try:
        gh = GitHubPATService(current_user.github_token)
        pr_info = gh.get_pr_info(project.github_repo_full_name, body.pr_number)
    except Exception as e:
        logger.error(f"Failed to fetch PR info: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch PR #{body.pr_number}: {str(e)}")

    # Check if we already have a run for this PR + head SHA
    existing_run = db.query(AnalysisRun).filter(
        AnalysisRun.project_id == project.id,
        AnalysisRun.pr_number == body.pr_number,
        AnalysisRun.head_sha == pr_info["head_sha"],
    ).first()
    if existing_run and existing_run.status == RunStatus.COMPLETED:
        return {
            "message": "Analysis already exists for this PR version",
            "run_id": existing_run.id,
            "status": existing_run.status.value,
            "already_exists": True,
        }

    # Create analysis run
    analysis_run = AnalysisRun(
        project_id=project.id,
        pr_number=pr_info["pr_number"],
        pr_url=pr_info["pr_url"],
        pr_title=pr_info["pr_title"],
        pr_author=pr_info["pr_author"],
        base_sha=pr_info["base_sha"],
        head_sha=pr_info["head_sha"],
        status=RunStatus.PENDING,
        run_metadata={"trigger": "manual"},
    )
    db.add(analysis_run)
    db.commit()
    db.refresh(analysis_run)

    # Run analysis — try Celery first, fall back to synchronous inline
    if settings.enable_background_tasks:
        try:
            analyze_pr_task.delay(analysis_run.id)
            return {
                "message": "Analysis queued",
                "run_id": analysis_run.id,
                "status": "pending",
                "already_exists": False,
            }
        except Exception as e:
            logger.warning(f"Celery unavailable, running inline: {e}")

    # Synchronous inline analysis (no Celery)
    try:
        _run_analysis_inline(analysis_run.id, current_user, db)
        db.refresh(analysis_run)
        return {
            "message": "Analysis completed",
            "run_id": analysis_run.id,
            "status": analysis_run.status.value,
            "already_exists": False,
        }
    except Exception as e:
        logger.error(f"Inline analysis failed: {e}", exc_info=True)
        analysis_run.status = RunStatus.FAILED
        analysis_run.error_message = str(e)
        analysis_run.completed_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


def _run_analysis_inline(run_id: int, user: User, db: Session):
    """Run PR analysis synchronously (no Celery) using user's PAT and API keys."""
    from app.services.github_pat_service import GitHubPATService
    from app.services.analyzer_service import AnalyzerService
    from app.services.llm_service import LLMService
    from app.models import FindingSeverity, FindingCategory
    from collections import defaultdict

    run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
    if not run:
        raise ValueError(f"Run {run_id} not found")

    run.status = RunStatus.RUNNING
    db.commit()

    project = run.project

    # Use PAT-based service
    gh = GitHubPATService(user.github_token)
    diff_data = gh.get_pr_diff(project.github_repo_full_name, run.pr_number)

    # Create status check (best-effort)
    gh.create_status_check(
        repo_full_name=project.github_repo_full_name,
        commit_sha=run.head_sha,
        state="pending",
        description="AI code review in progress...",
    )

    # Initialize services
    analyzer_service = AnalyzerService(project.config)
    user_keys = {
        "groq_api_key": user.groq_api_key,
        "openai_api_key": user.openai_api_key,
        "anthropic_api_key": user.anthropic_api_key,
        "google_api_key": user.google_api_key,
        "preferred_llm_provider": user.preferred_llm_provider,
    }
    llm_service = LLMService(user_keys=user_keys)

    # Run rule-based analysis
    logger.info("Running rule-based analysis...")
    rule_findings = analyzer_service.analyze_diff(diff_data)

    # Run AI analysis
    logger.info("Running AI analysis...")
    ai_findings = llm_service.analyze_diff(diff_data, rule_findings)

    # Merge and deduplicate
    all_findings = rule_findings + ai_findings

    # Deduplicate
    grouped = defaultdict(list)
    for finding in all_findings:
        key = (finding["file_path"], finding.get("line_number", 0))
        grouped[key].append(finding)

    deduplicated_findings = []
    severity_order = {
        FindingSeverity.CRITICAL: 0, FindingSeverity.HIGH: 1,
        FindingSeverity.MEDIUM: 2, FindingSeverity.LOW: 3,
    }
    for (file_path, line_number), group in grouped.items():
        if len(group) == 1:
            deduplicated_findings.append(group[0])
        else:
            group_sorted = sorted(group, key=lambda f: severity_order.get(f["severity"], 4))
            merged = group_sorted[0].copy()
            categories = set(f["category"] for f in group)
            if len(categories) > 1:
                merged["description"] += f"\n\nAdditional concerns: {', '.join(c.value for c in categories if c != merged['category'])}"
            deduplicated_findings.append(merged)

    # Save findings
    from app.services.semantic_search import get_semantic_search_service
    from app.services.code_sandbox import get_code_sandbox
    
    semantic_search = get_semantic_search_service()
    code_sandbox = get_code_sandbox()
    
    for finding_data in deduplicated_findings:
        auto_fix = ""
        if finding_data["severity"] in (FindingSeverity.CRITICAL, FindingSeverity.HIGH):
            try:
                file_patch = next(
                    (f.get("patch", "") for f in diff_data if f["filename"] == finding_data["file_path"]),
                    "",
                )
                if file_patch:
                    auto_fix = llm_service.generate_auto_fix(finding_data, file_patch)
            except Exception as e:
                logger.warning(f"Auto-fix generation failed: {e}")
        
        # Phase 2: Generate embedding
        embedding = None
        if semantic_search.is_available():
            try:
                embedding_text = f"{finding_data['title']}\n{finding_data['description']}"
                embedding_vector = semantic_search.embed_code(embedding_text)
                if embedding_vector is not None:
                    embedding = embedding_vector.tolist()
            except Exception as e:
                logger.warning(f"Embedding generation failed: {e}")

        finding = Finding(
            run_id=run.id,
            file_path=finding_data["file_path"],
            line_number=finding_data.get("line_number"),
            end_line_number=finding_data.get("end_line_number"),
            severity=finding_data["severity"],
            category=finding_data["category"],
            rule_id=finding_data.get("rule_id"),
            title=finding_data["title"],
            description=finding_data["description"],
            suggestion=finding_data.get("suggestion"),
            code_snippet=finding_data.get("code_snippet"),
            is_ai_generated=finding_data.get("is_ai_generated", 0),
            auto_fix_code=auto_fix if auto_fix else None,
            embedding=embedding,
            finding_metadata=finding_data.get("finding_metadata", {}),
        )
        db.add(finding)

    # Risk score
    try:
        risk_result = llm_service.compute_risk_score(diff_data, deduplicated_findings)
        run.risk_score = risk_result["score"]
        run.risk_breakdown = risk_result
    except Exception as e:
        logger.warning(f"Risk score computation failed: {e}")

    # PR summary
    try:
        run_meta = {
            "files_analyzed": len(diff_data),
            "findings_count": len(deduplicated_findings),
            "ai_findings": len(ai_findings),
        }
        pr_summary = llm_service.generate_pr_summary(diff_data, deduplicated_findings, run_meta)
        run.pr_summary = pr_summary if pr_summary else None
    except Exception as e:
        logger.warning(f"PR summary generation failed: {e}")

    # Update run
    run.run_metadata["files_analyzed"] = len(diff_data)
    run.run_metadata["findings_count"] = len(deduplicated_findings)
    run.run_metadata["rule_findings"] = len(rule_findings)
    run.run_metadata["ai_findings"] = len(ai_findings)
    run.completed_at = datetime.utcnow()
    run.status = RunStatus.COMPLETED
    
    # Phase 3B: Increment usage tracking
    from app.services.usage_service import UsageService
    
    total_lines = sum(len(file.get("patch", "").split("\n")) for file in diff_data)
    UsageService.increment_usage(
        user=run.project.owner,
        db=db,
        lines_analyzed=total_lines,
        findings_generated=len(deduplicated_findings),
    )
    
    db.commit()

    # Post results to PR (best-effort)
    try:
        critical = [f for f in deduplicated_findings if f["severity"] == FindingSeverity.CRITICAL]
        high = [f for f in deduplicated_findings if f["severity"] == FindingSeverity.HIGH]
        medium = [f for f in deduplicated_findings if f["severity"] == FindingSeverity.MEDIUM]

        summary = f"""## 🤖 AI Code Review Summary

**Analysis Results:**
- 🔴 Critical: {len(critical)}
- 🟠 High: {len(high)}
- 🟡 Medium: {len(medium)}
- Total Issues: {len(deduplicated_findings)}

---

"""
        if critical:
            summary += "### 🔴 Critical Issues\n\n"
            for f in critical[:3]:
                summary += f"- **{f['title']}** in `{f['file_path']}`\n"
                summary += f"  {f['description'][:100]}...\n\n"
        if high:
            summary += "### 🟠 High Priority Issues\n\n"
            for f in high[:3]:
                summary += f"- **{f['title']}** in `{f['file_path']}`\n"
                summary += f"  {f['description'][:100]}...\n\n"

        gh.post_pr_comment(project.github_repo_full_name, run.pr_number, summary)

        # Status check
        if len(critical) > 0:
            state, desc = "failure", f"❌ Found {len(critical)} critical issues"
        elif len(high) > 0:
            state, desc = "success", f"⚠️ Found {len(high)} high priority issues"
        else:
            state, desc = "success", "✅ No critical issues found"

        gh.create_status_check(
            repo_full_name=project.github_repo_full_name,
            commit_sha=run.head_sha,
            state=state,
            description=desc,
        )
    except Exception as e:
        logger.warning(f"Failed to post results to PR (non-fatal): {e}")

    logger.info(f"Inline analysis completed for run {run_id}")