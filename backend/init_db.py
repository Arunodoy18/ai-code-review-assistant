"""
Initialize database with all tables
"""
from app.database import engine, Base
from app.models import Project, AnalysisRun, Finding

def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    print("   - projects")
    print("   - analysis_runs")
    print("   - findings")

if __name__ == "__main__":
    init_db()
