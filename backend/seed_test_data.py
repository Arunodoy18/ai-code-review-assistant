"""
Seed test data for development and testing
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Project, AnalysisRun, Finding, RunStatus, FindingSeverity, FindingCategory

def seed_data():
    """Seed the database with test data"""
    db = SessionLocal()
    
    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(Finding).delete()
        db.query(AnalysisRun).delete()
        db.query(Project).delete()
        db.commit()
        
        # Create sample projects
        print("Creating sample projects...")
        projects = [
            Project(
                name="Hello-World",
                github_repo_full_name="octocat/Hello-World",
                github_installation_id=12345678,
                created_at=datetime.utcnow() - timedelta(days=30)
            ),
            Project(
                name="vscode",
                github_repo_full_name="microsoft/vscode",
                github_installation_id=12345679,
                created_at=datetime.utcnow() - timedelta(days=15)
            ),
            Project(
                name="cpython",
                github_repo_full_name="python/cpython",
                github_installation_id=12345680,
                created_at=datetime.utcnow() - timedelta(days=7)
            )
        ]
        db.add_all(projects)
        db.commit()
        print(f"✓ Created {len(projects)} projects")
        
        # Create sample analysis runs
        print("Creating sample analysis runs...")
        runs = []
        
        # Recent completed run with findings
        run1 = AnalysisRun(
            project_id=projects[0].id,
            pr_number=42,
            pr_title="Add user authentication with JWT tokens",
            pr_author="octocat",
            pr_url="https://github.com/octocat/Hello-World/pull/42",
            base_sha="abc123def455",
            head_sha="abc123def456",
            status=RunStatus.COMPLETED,
            run_metadata={
                "files_analyzed": 8,
                "findings_count": 12,
                "rule_findings": 7,
                "ai_findings": 5
            },
            started_at=datetime.utcnow() - timedelta(hours=2),
            completed_at=datetime.utcnow() - timedelta(hours=1, minutes=45)
        )
        runs.append(run1)
        
        # Running analysis
        run2 = AnalysisRun(
            project_id=projects[1].id,
            pr_number=1523,
            pr_title="Refactor extension host communication protocol",
            pr_author="bpasero",
            pr_url="https://github.com/microsoft/vscode/pull/1523",
            base_sha="def456ghi788",
            head_sha="def456ghi789",
            status=RunStatus.RUNNING,
            run_metadata={
                "files_analyzed": 15,
                "findings_count": 0,
                "rule_findings": 0,
                "ai_findings": 0
            },
            started_at=datetime.utcnow() - timedelta(minutes=5)
        )
        runs.append(run2)
        
        # Completed run with no issues
        run3 = AnalysisRun(
            project_id=projects[2].id,
            pr_number=203,
            pr_title="Update documentation for asyncio module",
            pr_author="gvanrossum",
            pr_url="https://github.com/python/cpython/pull/203",
            base_sha="ghi789jkl011",
            head_sha="ghi789jkl012",
            status=RunStatus.COMPLETED,
            run_metadata={
                "files_analyzed": 3,
                "findings_count": 0,
                "rule_findings": 0,
                "ai_findings": 0
            },
            started_at=datetime.utcnow() - timedelta(hours=5),
            completed_at=datetime.utcnow() - timedelta(hours=4, minutes=55)
        )
        runs.append(run3)
        
        # Failed analysis
        run4 = AnalysisRun(
            project_id=projects[0].id,
            pr_number=41,
            pr_title="Migrate database schema to Alembic",
            pr_author="developer123",
            pr_url="https://github.com/octocat/Hello-World/pull/41",
            base_sha="jkl012mno344",
            head_sha="jkl012mno345",
            status=RunStatus.FAILED,
            error_message="Failed to parse diff: Invalid unified diff format",
            run_metadata={
                "files_analyzed": 0,
                "findings_count": 0,
                "rule_findings": 0,
                "ai_findings": 0
            },
            started_at=datetime.utcnow() - timedelta(days=1),
            completed_at=datetime.utcnow() - timedelta(days=1, hours=-1)
        )
        runs.append(run4)
        
        # Older completed run with many findings
        run5 = AnalysisRun(
            project_id=projects[1].id,
            pr_number=1520,
            pr_title="Implement new settings editor UI",
            pr_author="sandy081",
            pr_url="https://github.com/microsoft/vscode/pull/1520",
            base_sha="mno345pqr677",
            head_sha="mno345pqr678",
            status=RunStatus.COMPLETED,
            run_metadata={
                "files_analyzed": 22,
                "findings_count": 28,
                "rule_findings": 18,
                "ai_findings": 10
            },
            started_at=datetime.utcnow() - timedelta(days=3),
            completed_at=datetime.utcnow() - timedelta(days=3, hours=-2)
        )
        runs.append(run5)
        
        db.add_all(runs)
        db.commit()
        print(f"✓ Created {len(runs)} analysis runs")
        
        # Create sample findings for run1
        print("Creating sample findings...")
        findings = []
        
        # Critical security finding
        findings.append(Finding(
            run_id=run1.id,
            file_path="src/auth/jwt_handler.py",
            line_number=42,
            severity=FindingSeverity.CRITICAL,
            category=FindingCategory.SECURITY,
            title="Hardcoded secret key detected",
            description="Found a hardcoded JWT secret key in the authentication handler. This is a critical security vulnerability that could allow attackers to forge authentication tokens.",
            suggestion="Store the secret key in environment variables or a secure key management service. Use: `secret_key = os.getenv('JWT_SECRET_KEY')`",
            code_snippet='SECRET_KEY = "my-super-secret-key-12345"',
            rule_id="SEC001",
            is_ai_generated=0,
            finding_metadata={"confidence": 1.0, "pattern": "hardcoded_secret"}
        ))
        
        # High severity bug
        findings.append(Finding(
            run_id=run1.id,
            file_path="src/auth/jwt_handler.py",
            line_number=67,
            severity=FindingSeverity.HIGH,
            category=FindingCategory.BUG,
            title="Missing error handling for expired tokens",
            description="The JWT decoding doesn't handle ExpiredSignatureError, which could cause the application to crash when processing expired tokens.",
            suggestion="Add a try-except block to catch ExpiredSignatureError and return an appropriate error response.",
            code_snippet='payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])',
            rule_id=None,
            is_ai_generated=1,
            finding_metadata={"confidence": 0.92, "model": "gpt-4"}
        ))
        
        # Medium performance issue
        findings.append(Finding(
            run_id=run1.id,
            file_path="src/auth/user_service.py",
            line_number=123,
            severity=FindingSeverity.MEDIUM,
            category=FindingCategory.PERFORMANCE,
            title="N+1 query detected in user lookup",
            description="The code is making individual database queries inside a loop, which is inefficient and can cause performance issues with large datasets.",
            suggestion="Use a single query with JOIN or IN clause to fetch all users at once: `users = db.query(User).filter(User.id.in_(user_ids)).all()`",
            code_snippet='for user_id in user_ids:\n    user = db.query(User).filter(User.id == user_id).first()\n    users.append(user)',
            rule_id="PERF003",
            is_ai_generated=0,
            finding_metadata={"confidence": 1.0, "pattern": "n_plus_one_query"}
        ))
        
        # Low priority best practice
        findings.append(Finding(
            run_id=run1.id,
            file_path="src/auth/validators.py",
            line_number=15,
            severity=FindingSeverity.LOW,
            category=FindingCategory.BEST_PRACTICE,
            title="Missing type hints on function parameters",
            description="Function parameters lack type hints, which reduces code clarity and prevents static type checking.",
            suggestion="Add type hints: `def validate_email(email: str) -> bool:`",
            code_snippet='def validate_email(email):\n    return "@" in email',
            rule_id="STYLE002",
            is_ai_generated=0,
            finding_metadata={"confidence": 1.0, "pattern": "missing_type_hints"}
        ))
        
        # AI-generated code quality suggestion
        findings.append(Finding(
            run_id=run1.id,
            file_path="src/auth/jwt_handler.py",
            line_number=89,
            severity=FindingSeverity.MEDIUM,
            category=FindingCategory.BEST_PRACTICE,
            title="Consider using dependency injection",
            description="The JWT handler is tightly coupled to the database session. Consider using dependency injection to make the code more testable and maintainable.",
            suggestion="Refactor to accept the database session as a parameter: `def verify_token(token: str, db: Session):`",
            code_snippet='def verify_token(token: str):\n    db = SessionLocal()\n    # ...',
            rule_id=None,
            is_ai_generated=1,
            finding_metadata={"confidence": 0.85, "model": "gpt-4"}
        ))
        
        # More findings for the same file
        findings.append(Finding(
            run_id=run1.id,
            file_path="src/auth/jwt_handler.py",
            line_number=105,
            severity=FindingSeverity.HIGH,
            category=FindingCategory.SECURITY,
            title="Weak JWT algorithm configuration",
            description="Using HS256 algorithm without proper key rotation mechanism. Consider implementing key rotation or using RS256 for better security.",
            suggestion="Implement key rotation mechanism or switch to RS256 algorithm with public/private key pair.",
            code_snippet='jwt.encode(payload, SECRET_KEY, algorithm="HS256")',
            rule_id="SEC005",
            is_ai_generated=0,
            finding_metadata={"confidence": 0.95, "pattern": "weak_jwt_algorithm"}
        ))
        
        # Findings in different files
        findings.append(Finding(
            run_id=run1.id,
            file_path="src/models/user.py",
            line_number=34,
            severity=FindingSeverity.MEDIUM,
            category=FindingCategory.SECURITY,
            title="Password stored without salt",
            description="The password hashing doesn't appear to use a salt, making it vulnerable to rainbow table attacks.",
            suggestion="Use bcrypt or argon2 with automatic salt generation: `password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())`",
            code_snippet='self.password_hash = hashlib.sha256(password.encode()).hexdigest()',
            rule_id="SEC003",
            is_ai_generated=0,
            finding_metadata={"confidence": 1.0, "pattern": "weak_password_hash"}
        ))
        
        findings.append(Finding(
            run_id=run1.id,
            file_path="src/api/auth_routes.py",
            line_number=56,
            severity=FindingSeverity.LOW,
            category=FindingCategory.BEST_PRACTICE,
            title="Missing API rate limiting",
            description="The authentication endpoint doesn't have rate limiting, which could make it vulnerable to brute force attacks.",
            suggestion="Add rate limiting middleware: `@limiter.limit('5 per minute')`",
            code_snippet='@router.post("/login")\nasync def login(credentials: LoginRequest):',
            rule_id=None,
            is_ai_generated=1,
            finding_metadata={"confidence": 0.78, "model": "gpt-4"}
        ))
        
        findings.append(Finding(
            run_id=run1.id,
            file_path="src/api/auth_routes.py",
            line_number=78,
            severity=FindingSeverity.LOW,
            category=FindingCategory.BEST_PRACTICE,
            title="Consider adding request logging",
            description="Authentication requests should be logged for security audit purposes.",
            suggestion="Add logging: `logger.info(f'Login attempt for user: {credentials.email}')`",
            code_snippet='@router.post("/login")\nasync def login(credentials: LoginRequest):',
            rule_id=None,
            is_ai_generated=1,
            finding_metadata={"confidence": 0.72, "model": "gpt-4"}
        ))
        
        findings.append(Finding(
            run_id=run1.id,
            file_path="src/utils/validators.py",
            line_number=23,
            severity=FindingSeverity.MEDIUM,
            category=FindingCategory.BUG,
            title="Regex vulnerable to ReDoS attack",
            description="The email validation regex pattern is susceptible to Regular Expression Denial of Service (ReDoS) attacks with specially crafted input.",
            suggestion="Use a simpler regex or a well-tested library like email-validator.",
            code_snippet='EMAIL_REGEX = r"^([a-zA-Z0-9_\\-\\.]+)@((\\[[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.)|(([a-zA-Z0-9\\-]+\\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\\]?)$"',
            rule_id="SEC008",
            is_ai_generated=0,
            finding_metadata={"confidence": 0.88, "pattern": "redos_vulnerable_regex"}
        ))
        
        findings.append(Finding(
            run_id=run1.id,
            file_path="tests/test_auth.py",
            line_number=145,
            severity=FindingSeverity.LOW,
            category=FindingCategory.BEST_PRACTICE,
            title="Test lacks assertion message",
            description="The assertion doesn't include a descriptive message, making test failures harder to debug.",
            suggestion="Add assertion message: `assert response.status_code == 200, 'Login should return 200 for valid credentials'`",
            code_snippet='assert response.status_code == 200',
            rule_id="TEST001",
            is_ai_generated=0,
            finding_metadata={"confidence": 1.0, "pattern": "missing_assertion_message"}
        ))
        
        findings.append(Finding(
            run_id=run1.id,
            file_path="src/config.py",
            line_number=12,
            severity=FindingSeverity.CRITICAL,
            category=FindingCategory.SECURITY,
            title="Debug mode enabled in configuration",
            description="Debug mode is hardcoded to True, which can expose sensitive information in production environments.",
            suggestion="Use environment variable: `DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'`",
            code_snippet='DEBUG = True',
            rule_id="SEC002",
            is_ai_generated=0,
            finding_metadata={"confidence": 1.0, "pattern": "debug_enabled"}
        ))
        
        db.add_all(findings)
        db.commit()
        print(f"✓ Created {len(findings)} findings")
        
        # Create findings for run5 (older run with many findings)
        print("Creating additional findings for run5...")
        run5_findings = []
        
        severities = [FindingSeverity.CRITICAL, FindingSeverity.HIGH, FindingSeverity.MEDIUM, FindingSeverity.LOW]
        categories = [FindingCategory.SECURITY, FindingCategory.BUG, FindingCategory.PERFORMANCE, FindingCategory.BEST_PRACTICE]
        
        for i in range(28):
            run5_findings.append(Finding(
                run_id=run5.id,
                file_path=f"src/settings/editor_{i % 5}.ts",
                line_number=10 + i * 5,
                severity=severities[i % 4],
                category=categories[i % 4],
                title=f"Code issue #{i + 1} in settings editor",
                description=f"This is a sample finding for the settings editor implementation. Issue type: {categories[i % 4].value}",
                suggestion=f"Apply fix for issue #{i + 1}",
                code_snippet=f'// Code snippet {i + 1}\nconst setting = getSetting("value");',
                rule_id=f"RULE{i:03d}" if i % 2 == 0 else None,
                is_ai_generated=i % 2,
                finding_metadata={"confidence": 0.8 + (i % 20) / 100}
            ))
        
        db.add_all(run5_findings)
        db.commit()
        print(f"✓ Created {len(run5_findings)} additional findings for run5")
        
        print("\n✅ Database seeded successfully!")
        print(f"\nSummary:")
        print(f"  - Projects: {len(projects)}")
        print(f"  - Analysis Runs: {len(runs)}")
        print(f"  - Findings: {len(findings) + len(run5_findings)}")
        print(f"\nYou can now view the data at: http://localhost:5173")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding test data...")
    seed_data()
