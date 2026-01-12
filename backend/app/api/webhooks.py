from fastapi import APIRouter, Request, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, AnalysisRun, RunStatus
from app.services.github_service import verify_github_signature, parse_pr_event
from app.tasks.analysis import analyze_pr_task
from app.config import settings
import logging
import hmac
import hashlib

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Receive GitHub webhook events for pull requests
    """
    if not settings.enable_github_webhooks or not settings.enable_github_integration:
        logger.info("GitHub webhook received but integration is disabled in local configuration")
        raise HTTPException(status_code=503, detail="GitHub webhooks are disabled for this environment")

    try:
        body = await request.body()
        
        # Verify signature
        if not verify_github_signature(body, x_hub_signature_256):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse event
        payload = await request.json()
        
        # Only handle pull request events
        if x_github_event not in ["pull_request", "pull_request_review"]:
            logger.info(f"Ignoring event type: {x_github_event}")
            return {"message": "Event ignored"}
        
        # Check action
        action = payload.get("action")
        if action not in ["opened", "synchronize", "reopened"]:
            logger.info(f"Ignoring PR action: {action}")
            return {"message": "Action ignored"}
        
        # Extract PR data
        pr_data = parse_pr_event(payload)
        
        # Get or create project
        repo_full_name = pr_data["repo_full_name"]
        project = db.query(Project).filter(
            Project.github_repo_full_name == repo_full_name
        ).first()
        
        if not project:
            # Create new project
            installation_id = payload.get("installation", {}).get("id")
            project = Project(
                name=pr_data["repo_name"],
                github_repo_full_name=repo_full_name,
                github_installation_id=installation_id,
                config={}
            )
            db.add(project)
            db.commit()
            db.refresh(project)
        
        # Create analysis run
        analysis_run = AnalysisRun(
            project_id=project.id,
            pr_number=pr_data["pr_number"],
            pr_url=pr_data["pr_url"],
            pr_title=pr_data["pr_title"],
            pr_author=pr_data["pr_author"],
            base_sha=pr_data["base_sha"],
            head_sha=pr_data["head_sha"],
            status=RunStatus.PENDING,
            run_metadata={"action": action}
        )
        db.add(analysis_run)
        db.commit()
        db.refresh(analysis_run)
        
        # Queue analysis task
        if settings.enable_background_tasks:
            analyze_pr_task.delay(analysis_run.id)
        else:
            logger.info("Background task queue disabled; analysis will not run automatically")
        
        logger.info(f"Queued analysis for PR #{pr_data['pr_number']} in {repo_full_name}")
        
        return {
            "message": "Analysis queued",
            "run_id": analysis_run.id,
            "pr_number": pr_data["pr_number"]
        }
        
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
