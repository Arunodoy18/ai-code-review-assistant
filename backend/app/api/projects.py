from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, User
from app.config import settings
from app.services.auth_service import get_current_user
from app.services.github_pat_service import GitHubPATService
from pydantic import BaseModel
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    github_repo_full_name: str
    github_installation_id: Optional[int] = None
    config: Optional[Dict] = {}


class AddRepoRequest(BaseModel):
    repo_full_name: str  # e.g. "owner/repo"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict] = None


@router.get("/")
async def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List projects owned by the authenticated user."""
    try:
        projects = db.query(Project).filter(Project.owner_id == current_user.id).order_by(Project.created_at.desc()).all()
        return {
            "success": True,
            "count": len(projects),
            "data": projects
        }
    except Exception as e:
        logger.error(f"Error fetching projects: {e}", exc_info=True)
        return {
            "success": False,
            "count": 0,
            "data": [],
            "error": str(e) if settings.environment == "development" else "Internal server error"
        }


@router.get("/{project_id}")
async def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get project by ID (must belong to current user)"""
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/")
async def create_project(project_data: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new project owned by the authenticated user"""
    # Check if project already exists for this user
    existing = db.query(Project).filter(
        Project.github_repo_full_name == project_data.github_repo_full_name,
        Project.owner_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Project already exists")
    
    project = Project(
        name=project_data.name,
        github_repo_full_name=project_data.github_repo_full_name,
        github_installation_id=project_data.github_installation_id,
        config=project_data.config or {},
        owner_id=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.post("/add-repo")
async def add_repo(
    body: AddRepoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a GitHub repository by name. Validates access using the user's PAT."""
    if not current_user.github_token:
        raise HTTPException(
            status_code=400,
            detail="Please configure your GitHub Personal Access Token in Settings first.",
        )

    repo_full_name = body.repo_full_name.strip()
    if "/" not in repo_full_name or len(repo_full_name.split("/")) != 2:
        raise HTTPException(status_code=400, detail="Invalid repo format. Use owner/repo")

    # Check duplicate
    existing = db.query(Project).filter(
        Project.github_repo_full_name == repo_full_name,
        Project.owner_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Repository already added")

    # Validate repo access with user's PAT
    try:
        gh = GitHubPATService(current_user.github_token)
        repo_info = gh.validate_repo_access(repo_full_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub API error: {str(e)}")

    if not repo_info.get("accessible"):
        raise HTTPException(
            status_code=403,
            detail=f"Cannot access repository: {repo_info.get('error', 'Unknown error')}. Check your PAT permissions.",
        )

    # Create project
    project = Project(
        name=repo_full_name.split("/")[1],
        github_repo_full_name=repo_info["full_name"],
        github_installation_id=None,
        config={},
        owner_id=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    logger.info(f"User {current_user.id} added repo {repo_full_name}")
    return {
        "project": project,
        "repo_info": repo_info,
    }


@router.get("/{project_id}/prs")
async def list_project_prs(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List open PRs for a project (uses the user's GitHub PAT)."""
    project = db.query(Project).filter(
        Project.id == project_id, Project.owner_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not current_user.github_token:
        raise HTTPException(status_code=400, detail="GitHub token not configured")

    try:
        gh = GitHubPATService(current_user.github_token)
        prs = gh.list_open_prs(project.github_repo_full_name)
        return {"prs": prs, "count": len(prs)}
    except Exception as e:
        logger.error(f"Failed to list PRs for {project.github_repo_full_name}: {e}")
        raise HTTPException(status_code=500, detail=f"GitHub API error: {str(e)}")


@router.patch("/{project_id}")
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project configuration (must belong to current user)"""
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a project (must belong to current user)"""
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted"}
