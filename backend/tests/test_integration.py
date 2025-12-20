"""
Integration tests for the analysis pipeline
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Project, AnalysisRun, Finding, RunStatus
from app.services.analyzer_service import AnalyzerService
from app.services.diff_parser import DiffParser
from tests.fixtures.mock_data import MOCK_PR_DATA, EXPECTED_ANALYSIS_RESULTS


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_project(db_session):
    """Create a test project"""
    project = Project(
        name="test-repo",
        github_repo_full_name="test-org/test-repo",
        github_installation_id=11111111,
        config={}
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


class TestAnalysisPipeline:
    """Test the complete analysis pipeline"""
    
    def test_security_issues_detection(self, db_session, test_project):
        """Test detection of security vulnerabilities"""
        # Arrange
        pr_data = MOCK_PR_DATA["pr_with_security_issues"]
        analyzer = AnalyzerService()
        
        # Act
        findings = []
        for line_num, line in enumerate(pr_data["diff"].split("\n"), start=1):
            if line.startswith("+") and not line.startswith("+++"):
                line_findings = analyzer.analyze_line(
                    line[1:],  # Remove the + prefix
                    "app/auth.py",
                    line_num,
                    "python"
                )
                findings.extend(line_findings)
        
        # Assert
        assert len(findings) >= 4, f"Expected at least 4 security findings, got {len(findings)}"
        
        # Check for specific security issues
        rule_ids = [f.rule_id for f in findings]
        assert "security.hardcoded_secrets" in rule_ids
        assert "security.sql_injection" in rule_ids
        assert "security.command_injection" in rule_ids
        
        # Verify severity levels
        critical_findings = [f for f in findings if f.severity == "critical"]
        assert len(critical_findings) >= 2, "Should have critical security findings"
    
    def test_code_quality_issues_detection(self, db_session, test_project):
        """Test detection of code quality issues"""
        # Arrange
        pr_data = MOCK_PR_DATA["pr_with_code_quality_issues"]
        analyzer = AnalyzerService()
        
        # Act
        findings = []
        for line_num, line in enumerate(pr_data["diff"].split("\n"), start=1):
            if line.startswith("+") and not line.startswith("+++"):
                line_findings = analyzer.analyze_line(
                    line[1:],
                    "app/processor.py",
                    line_num,
                    "python"
                )
                findings.extend(line_findings)
        
        # Assert
        assert len(findings) >= 3, f"Expected at least 3 quality findings, got {len(findings)}"
        
        # Check for specific quality issues
        rule_ids = [f.rule_id for f in findings]
        assert any("quality" in rid or "best_practice" in rid for rid in rule_ids)
    
    def test_performance_issues_detection(self, db_session, test_project):
        """Test detection of performance issues"""
        # Arrange
        pr_data = MOCK_PR_DATA["pr_with_performance_issues"]
        analyzer = AnalyzerService()
        
        # Act
        findings = []
        for line_num, line in enumerate(pr_data["diff"].split("\n"), start=1):
            if line.startswith("+") and not line.startswith("+++"):
                line_findings = analyzer.analyze_line(
                    line[1:],
                    "app/database.py",
                    line_num,
                    "python"
                )
                findings.extend(line_findings)
        
        # Assert
        assert len(findings) >= 1, f"Expected at least 1 performance finding, got {len(findings)}"
        
        # Check for N+1 query detection
        rule_ids = [f.rule_id for f in findings]
        assert any("performance" in rid for rid in rule_ids)
    
    def test_clean_code_no_issues(self, db_session, test_project):
        """Test that clean code produces minimal findings"""
        # Arrange
        pr_data = MOCK_PR_DATA["pr_clean_code"]
        analyzer = AnalyzerService()
        
        # Act
        findings = []
        for line_num, line in enumerate(pr_data["diff"].split("\n"), start=1):
            if line.startswith("+") and not line.startswith("+++"):
                line_findings = analyzer.analyze_line(
                    line[1:],
                    "app/utils.py",
                    line_num,
                    "python"
                )
                findings.extend(line_findings)
        
        # Assert
        # Well-written code should have zero or very few findings
        assert len(findings) <= 1, f"Clean code should have minimal findings, got {len(findings)}"
    
    def test_diff_parser_hunks(self):
        """Test diff parser hunk extraction"""
        # Arrange
        pr_data = MOCK_PR_DATA["pr_with_security_issues"]
        parser = DiffParser()
        
        # Act
        hunks, added_lines, removed_lines, context = parser.parse_patch(pr_data["diff"])
        
        # Assert
        assert len(hunks) > 0, "Should extract at least one hunk"
        assert len(added_lines) > 0, "Should have added lines"
        assert "app/auth.py" in pr_data["diff"]
    
    def test_diff_parser_line_numbers(self):
        """Test diff parser line number extraction"""
        # Arrange
        pr_data = MOCK_PR_DATA["pr_with_security_issues"]
        parser = DiffParser()
        
        # Act
        line_numbers = parser.get_changed_line_numbers(pr_data["diff"])
        
        # Assert
        assert len(line_numbers) > 0, "Should extract line numbers"
        assert all(isinstance(num, int) for num in line_numbers)
    
    def test_analysis_run_creation(self, db_session, test_project):
        """Test creating an analysis run"""
        # Arrange
        pr_data = MOCK_PR_DATA["pr_with_security_issues"]
        
        # Act
        run = AnalysisRun(
            project_id=test_project.id,
            pr_number=pr_data["number"],
            pr_url=pr_data["url"],
            pr_title=pr_data["title"],
            pr_author=pr_data["author"],
            base_sha=pr_data["base_sha"],
            head_sha=pr_data["head_sha"],
            status=RunStatus.COMPLETED,
            run_metadata={
                "files_analyzed": len(pr_data["files"]),
                "findings_count": 5
            }
        )
        db_session.add(run)
        db_session.commit()
        
        # Assert
        assert run.id is not None
        assert run.status == RunStatus.COMPLETED
        assert run.project_id == test_project.id
    
    def test_findings_creation(self, db_session, test_project):
        """Test creating findings"""
        # Arrange
        run = AnalysisRun(
            project_id=test_project.id,
            pr_number=101,
            pr_url="https://github.com/test/test/pull/101",
            pr_title="Test PR",
            pr_author="tester",
            base_sha="abc123",
            head_sha="def456",
            status=RunStatus.COMPLETED
        )
        db_session.add(run)
        db_session.commit()
        
        # Act
        finding = Finding(
            run_id=run.id,
            file_path="app/auth.py",
            line_number=10,
            severity="critical",
            category="security",
            rule_id="security.sql_injection",
            title="SQL Injection Vulnerability",
            description="Detected SQL injection risk",
            suggestion="Use parameterized queries",
            code_snippet="query = f\"SELECT * FROM users WHERE id='{user_id}'\"",
            is_ai_generated=0
        )
        db_session.add(finding)
        db_session.commit()
        
        # Assert
        assert finding.id is not None
        assert finding.run_id == run.id
        assert finding.severity == "critical"
    
    def test_findings_by_severity(self, db_session, test_project):
        """Test querying findings by severity"""
        # Arrange
        run = AnalysisRun(
            project_id=test_project.id,
            pr_number=101,
            pr_url="https://github.com/test/test/pull/101",
            pr_title="Test PR",
            pr_author="tester",
            base_sha="abc123",
            head_sha="def456",
            status=RunStatus.COMPLETED
        )
        db_session.add(run)
        db_session.commit()
        
        # Create findings with different severities
        severities = ["critical", "high", "medium", "low"]
        for i, severity in enumerate(severities):
            finding = Finding(
                run_id=run.id,
                file_path=f"app/file{i}.py",
                line_number=i,
                severity=severity,
                category="security",
                rule_id=f"test.rule{i}",
                title=f"Test Finding {i}",
                description="Test",
                is_ai_generated=0
            )
            db_session.add(finding)
        db_session.commit()
        
        # Act
        critical_findings = db_session.query(Finding).filter(
            Finding.run_id == run.id,
            Finding.severity == "critical"
        ).all()
        
        # Assert
        assert len(critical_findings) == 1
        assert critical_findings[0].severity == "critical"


class TestConfigurationIntegration:
    """Test configuration system integration"""
    
    def test_project_config_persistence(self, db_session, test_project):
        """Test saving and loading project configuration"""
        # Arrange
        config = {
            "disabled_rules": ["quality.console_log"],
            "analysis_config": {
                "enable_ai_analysis": True,
                "min_severity_to_comment": "high"
            }
        }
        
        # Act
        test_project.config = config
        db_session.commit()
        
        # Reload project
        db_session.expire(test_project)
        loaded_project = db_session.query(Project).filter(
            Project.id == test_project.id
        ).first()
        
        # Assert
        assert loaded_project.config == config
        assert "quality.console_log" in loaded_project.config["disabled_rules"]
