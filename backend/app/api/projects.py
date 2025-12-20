from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project
from pydantic import BaseModel
from typing import Optional, Dict

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
async def list_projects(db: Session = Depends(get_db)):
    """List all projects"""
    projects = db.query(Project).all()
    return projects


@router.get("/{project_id}")
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get project by ID"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/")
async def create_project(project_data: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project"""
    # Check if project already exists
    existing = db.query(Project).filter(
        Project.github_repo_full_name == project_data.github_repo_full_name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Project already exists")
    
    project = Project(**project_data.dict())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.patch("/{project_id}")
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update project configuration"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted"}
