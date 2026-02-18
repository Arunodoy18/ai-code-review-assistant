from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class RunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class FindingSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingCategory(str, enum.Enum):
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    BEST_PRACTICE = "best_practice"
    DOCUMENTATION = "documentation"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    projects = relationship("Project", back_populates="owner")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    github_repo_full_name = Column(String, unique=True, nullable=False, index=True)  # owner/repo
    github_installation_id = Column(Integer, nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    config = Column(JSON, default={})  # Rules, thresholds, etc.
    dismissed_patterns = Column(JSON, default=[])  # Learned false-positive patterns
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="projects")
    runs = relationship("AnalysisRun", back_populates="project")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    pr_number = Column(Integer, nullable=False, index=True)
    pr_url = Column(String, nullable=False)
    pr_title = Column(String)
    pr_author = Column(String, index=True)
    base_sha = Column(String, nullable=False)
    head_sha = Column(String, nullable=False, index=True)
    status = Column(SQLEnum(RunStatus), default=RunStatus.PENDING, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True, index=True)
    error_message = Column(Text, nullable=True)
    run_metadata = Column(JSON, default={})  # Changed files count, lines analyzed, etc.
    risk_score = Column(Float, nullable=True)  # 0-100 PR risk score
    risk_breakdown = Column(JSON, default={})  # Detailed risk breakdown
    pr_summary = Column(Text, nullable=True)  # Natural language PR summary for non-tech stakeholders

    project = relationship("Project", back_populates="runs")
    findings = relationship("Finding", back_populates="run", cascade="all, delete-orphan")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("analysis_runs.id"), nullable=False, index=True)
    file_path = Column(String, nullable=False, index=True)
    line_number = Column(Integer, nullable=True)
    end_line_number = Column(Integer, nullable=True)
    severity = Column(SQLEnum(FindingSeverity), nullable=False, index=True)
    category = Column(SQLEnum(FindingCategory), nullable=False, index=True)
    rule_id = Column(String, nullable=True, index=True)  # e.g., "eslint:no-unused-vars", "AI:logic-error"
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    suggestion = Column(Text, nullable=True)
    code_snippet = Column(Text, nullable=True)
    is_ai_generated = Column(Integer, default=0, index=True)  # 0=rule-based, 1=AI
    is_resolved = Column(Integer, default=0, index=True)
    is_dismissed = Column(Integer, default=0, index=True)  # Learning system: user dismissed this finding
    auto_fix_code = Column(Text, nullable=True)  # AI-generated fix patch
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    finding_metadata = Column(JSON, default={})  # Additional context

    run = relationship("AnalysisRun", back_populates="findings")
