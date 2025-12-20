"""
Add database indexes for performance optimization

This script adds indexes to frequently queried columns to improve query performance.
Run this after updating the models.py with new indexes.
"""

from app.database import engine
from sqlalchemy import text

def add_indexes():
    """Add indexes to existing database tables"""
    
    with engine.begin() as conn:
        # Check if indexes already exist before creating
        indexes = [
            # Project indexes
            ("idx_projects_name", "CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name)"),
            ("idx_projects_github_repo", "CREATE INDEX IF NOT EXISTS idx_projects_github_repo ON projects(github_repo_full_name)"),
            ("idx_projects_installation", "CREATE INDEX IF NOT EXISTS idx_projects_installation ON projects(github_installation_id)"),
            ("idx_projects_created", "CREATE INDEX IF NOT EXISTS idx_projects_created ON projects(created_at)"),
            
            # AnalysisRun indexes
            ("idx_runs_project", "CREATE INDEX IF NOT EXISTS idx_runs_project ON analysis_runs(project_id)"),
            ("idx_runs_pr_number", "CREATE INDEX IF NOT EXISTS idx_runs_pr_number ON analysis_runs(pr_number)"),
            ("idx_runs_author", "CREATE INDEX IF NOT EXISTS idx_runs_author ON analysis_runs(pr_author)"),
            ("idx_runs_head_sha", "CREATE INDEX IF NOT EXISTS idx_runs_head_sha ON analysis_runs(head_sha)"),
            ("idx_runs_status", "CREATE INDEX IF NOT EXISTS idx_runs_status ON analysis_runs(status)"),
            ("idx_runs_started", "CREATE INDEX IF NOT EXISTS idx_runs_started ON analysis_runs(started_at)"),
            ("idx_runs_completed", "CREATE INDEX IF NOT EXISTS idx_runs_completed ON analysis_runs(completed_at)"),
            
            # Finding indexes
            ("idx_findings_run", "CREATE INDEX IF NOT EXISTS idx_findings_run ON findings(run_id)"),
            ("idx_findings_file", "CREATE INDEX IF NOT EXISTS idx_findings_file ON findings(file_path)"),
            ("idx_findings_severity", "CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity)"),
            ("idx_findings_category", "CREATE INDEX IF NOT EXISTS idx_findings_category ON findings(category)"),
            ("idx_findings_rule", "CREATE INDEX IF NOT EXISTS idx_findings_rule ON findings(rule_id)"),
            ("idx_findings_ai", "CREATE INDEX IF NOT EXISTS idx_findings_ai ON findings(is_ai_generated)"),
            ("idx_findings_resolved", "CREATE INDEX IF NOT EXISTS idx_findings_resolved ON findings(is_resolved)"),
            ("idx_findings_created", "CREATE INDEX IF NOT EXISTS idx_findings_created ON findings(created_at)"),
            
            # Composite indexes for common queries
            ("idx_runs_project_status", "CREATE INDEX IF NOT EXISTS idx_runs_project_status ON analysis_runs(project_id, status)"),
            ("idx_findings_run_severity", "CREATE INDEX IF NOT EXISTS idx_findings_run_severity ON findings(run_id, severity)"),
            ("idx_findings_run_category", "CREATE INDEX IF NOT EXISTS idx_findings_run_category ON findings(run_id, category)"),
        ]
        
        print("Adding database indexes for performance optimization...")
        for idx_name, sql in indexes:
            try:
                conn.execute(text(sql))
                print(f"✓ Created index: {idx_name}")
            except Exception as e:
                print(f"✗ Error creating {idx_name}: {e}")
        
        print("\nIndexes added successfully!")


if __name__ == "__main__":
    print("Starting index migration...")
    add_indexes()
    print("Migration complete!")
