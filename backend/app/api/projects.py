from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, User
from app.config import settings
from app.services.auth_service import get_current_user
from pydantic import BaseModel
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    github_repo_full_name: str
    github_installation_id: int
    config: Optional[Dict] = {}


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
    
    project = Project(**project_data.dict(), owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


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
