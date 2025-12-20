"""
Configuration schemas for project settings and rule management
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from enum import Enum


class RuleSeverity(str, Enum):
    """Rule severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RuleCategory(str, Enum):
    """Rule categories"""
    SECURITY = "security"
    BUG = "bug"
    PERFORMANCE = "performance"
    STYLE = "style"
    BEST_PRACTICE = "best_practice"
    DOCUMENTATION = "documentation"


class RuleConfig(BaseModel):
    """Configuration for a single rule"""
    rule_id: str = Field(..., description="Unique rule identifier")
    enabled: bool = Field(default=True, description="Whether rule is active")
    severity: Optional[RuleSeverity] = Field(None, description="Override default severity")
    custom_message: Optional[str] = Field(None, description="Custom message template")


class AnalysisConfig(BaseModel):
    """Analysis configuration settings"""
    enable_ai_analysis: bool = Field(default=True, description="Enable LLM-based analysis")
    ai_model: str = Field(default="gpt-4", description="AI model to use (gpt-4, claude-3)")
    max_files_per_analysis: int = Field(default=50, description="Maximum files to analyze")
    max_lines_per_file: int = Field(default=500, description="Maximum lines per file for AI")
    min_severity_to_comment: RuleSeverity = Field(
        default=RuleSeverity.MEDIUM,
        description="Minimum severity to post PR comments"
    )
    auto_resolve_on_fix: bool = Field(
        default=True,
        description="Auto-resolve findings when code is fixed"
    )


class ProjectConfigSchema(BaseModel):
    """Complete project configuration"""
    project_id: int
    enabled_rules: List[str] = Field(
        default_factory=list,
        description="List of enabled rule IDs (empty = all enabled)"
    )
    disabled_rules: List[str] = Field(
        default_factory=list,
        description="List of disabled rule IDs"
    )
    rule_configs: Dict[str, RuleConfig] = Field(
        default_factory=dict,
        description="Per-rule configuration overrides"
    )
    analysis_config: AnalysisConfig = Field(
        default_factory=AnalysisConfig,
        description="General analysis settings"
    )
    exclude_paths: List[str] = Field(
        default_factory=lambda: ["**/node_modules/**", "**/dist/**", "**/build/**"],
        description="Glob patterns for excluded paths"
    )
    include_paths: List[str] = Field(
        default_factory=lambda: ["**/*.py", "**/*.js", "**/*.ts", "**/*.tsx", "**/*.java"],
        description="Glob patterns for included file types"
    )


class ProjectConfigUpdate(BaseModel):
    """Schema for updating project configuration"""
    enabled_rules: Optional[List[str]] = None
    disabled_rules: Optional[List[str]] = None
    rule_configs: Optional[Dict[str, RuleConfig]] = None
    analysis_config: Optional[AnalysisConfig] = None
    exclude_paths: Optional[List[str]] = None
    include_paths: Optional[List[str]] = None


class RuleDefinition(BaseModel):
    """Definition of an available rule"""
    rule_id: str
    name: str
    description: str
    category: RuleCategory
    default_severity: RuleSeverity
    languages: List[str] = Field(default_factory=list, description="Applicable languages")
    configurable: bool = Field(default=True, description="Can be configured per project")
    requires_ai: bool = Field(default=False, description="Requires AI/LLM analysis")
