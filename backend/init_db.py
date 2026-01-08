"""Initialize database tables"""
from app.database import engine, Base
from app.models import Project, AnalysisRun, Finding

def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")

if __name__ == "__main__":
    init_db()
