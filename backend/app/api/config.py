"""
Configuration management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.config_service import ConfigurationService
from app.schemas.config import (
    ProjectConfigSchema, 
    ProjectConfigUpdate,
    RuleDefinition,
    RuleCategory
)
from typing import List, Optional

router = APIRouter(prefix="/config", tags=["Configuration"])


@router.get("/rules", response_model=List[RuleDefinition])
async def list_available_rules(
    category: Optional[str] = Query(None, description="Filter by category"),
    language: Optional[str] = Query(None, description="Filter by language"),
    db: Session = Depends(get_db)
):
    """Get list of all available analysis rules"""
    config_service = ConfigurationService(db)
    return config_service.get_all_rules(category=category, language=language)


@router.get("/rules/{rule_id}", response_model=RuleDefinition)
async def get_rule_definition(rule_id: str, db: Session = Depends(get_db)):
    """Get details of a specific rule"""
    config_service = ConfigurationService(db)
    rule = config_service.get_rule_definition(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")
    return rule


@router.get("/projects/{project_id}", response_model=ProjectConfigSchema)
async def get_project_configuration(project_id: int, db: Session = Depends(get_db)):
    """Get configuration for a project"""
    config_service = ConfigurationService(db)
    try:
        return config_service.get_project_config(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/projects/{project_id}", response_model=ProjectConfigSchema)
async def update_project_configuration(
    project_id: int,
    config_update: ProjectConfigUpdate,
    db: Session = Depends(get_db)
):
    """Update project configuration"""
    config_service = ConfigurationService(db)
    try:
        updates = config_update.dict(exclude_unset=True)
        return config_service.update_project_config(project_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/projects/{project_id}/enabled-rules", response_model=List[str])
async def get_enabled_rules(project_id: int, db: Session = Depends(get_db)):
    """Get list of enabled rule IDs for a project"""
    config_service = ConfigurationService(db)
    try:
        return config_service.get_enabled_rules(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/projects/{project_id}/rules/{rule_id}/enable")
async def enable_rule(project_id: int, rule_id: str, db: Session = Depends(get_db)):
    """Enable a specific rule for a project"""
    config_service = ConfigurationService(db)
    
    # Verify rule exists
    if not config_service.get_rule_definition(rule_id):
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")
    
    try:
        config = config_service.get_project_config(project_id)
        
        # Remove from disabled list
        disabled = set(config.disabled_rules)
        disabled.discard(rule_id)
        
        # Add to enabled list if using whitelist mode
        enabled = set(config.enabled_rules) if config.enabled_rules else set()
        if config.enabled_rules:
            enabled.add(rule_id)
        
        updates = {
            "enabled_rules": list(enabled) if config.enabled_rules else [],
            "disabled_rules": list(disabled)
        }
        
        return config_service.update_project_config(project_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/projects/{project_id}/rules/{rule_id}/disable")
async def disable_rule(project_id: int, rule_id: str, db: Session = Depends(get_db)):
    """Disable a specific rule for a project"""
    config_service = ConfigurationService(db)
    
    # Verify rule exists
    if not config_service.get_rule_definition(rule_id):
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")
    
    try:
        config = config_service.get_project_config(project_id)
        
        # Remove from enabled list
        enabled = set(config.enabled_rules) if config.enabled_rules else set()
        enabled.discard(rule_id)
        
        # Add to disabled list
        disabled = set(config.disabled_rules)
        disabled.add(rule_id)
        
        updates = {
            "enabled_rules": list(enabled) if config.enabled_rules else [],
            "disabled_rules": list(disabled)
        }
        
        return config_service.update_project_config(project_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/projects/{project_id}/rules/{rule_id}/status")
async def check_rule_status(project_id: int, rule_id: str, db: Session = Depends(get_db)):
    """Check if a rule is enabled for a project"""
    config_service = ConfigurationService(db)
    
    if not config_service.get_rule_definition(rule_id):
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")
    
    try:
        is_enabled = config_service.is_rule_enabled(project_id, rule_id)
        severity = config_service.get_rule_severity(project_id, rule_id)
        
        return {
            "project_id": project_id,
            "rule_id": rule_id,
            "enabled": is_enabled,
            "severity": severity
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
