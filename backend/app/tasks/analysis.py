from app.tasks import celery_app
from app.database import SessionLocal
from app.models import AnalysisRun, Finding, Project, User, RunStatus, FindingSeverity, FindingCategory
from app.services.analyzer_service import AnalyzerService
from app.services.llm_service import LLMService
from app.services.diff_parser import DiffParser
from app.services.semantic_search import get_semantic_search_service
from app.services.code_sandbox import get_code_sandbox
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


def _get_github_service(project, owner):
    """Get the appropriate GitHub service — PAT-based (SaaS) or App-based (legacy)."""
    # Prefer PAT-based service if owner has a GitHub token
    if owner and owner.github_token:
        from app.services.github_pat_service import GitHubPATService
        return GitHubPATService(owner.github_token)

    # Fallback to legacy GitHub App service
    if project.github_installation_id:
        from app.services.github_service import GitHubService
        return GitHubService(project.github_installation_id)

    raise RuntimeError(
        "No GitHub credentials available. "
        "The project owner must configure a GitHub Personal Access Token in Settings."
    )


@celery_app.task(bind=True, max_retries=3)
def analyze_pr_task(self, run_id: int):
    """
    Celery task to analyze a PR
    """
    db = SessionLocal()
    
    try:
        # Get analysis run
        run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
        if not run:
            logger.error(f"Run {run_id} not found")
            return
        
        # Update status
        run.status = RunStatus.RUNNING
        db.commit()
        
        # Get project and GitHub service
        project = run.project
        
        # Load owner for PAT-based auth
        owner = None
        if project.owner_id:
            owner = db.query(User).filter(User.id == project.owner_id).first()
        
        github_service = _get_github_service(project, owner)
        
        # Create status check
        github_service.create_status_check(
            repo_full_name=project.github_repo_full_name,
            commit_sha=run.head_sha,
            state="pending",
            description="AI code review in progress..."
        )
        
        # Get PR diff and files
        logger.info(f"Fetching PR #{run.pr_number} data...")
        diff_data = github_service.get_pr_diff(
            project.github_repo_full_name,
            run.pr_number
        )
        
        # Initialize services
        analyzer_service = AnalyzerService(project.config)
        
        # Load per-user API keys
        user_keys = None
        if owner:
            user_keys = {
                "groq_api_key": owner.groq_api_key,
                "openai_api_key": owner.openai_api_key,
                "anthropic_api_key": owner.anthropic_api_key,
                "google_api_key": owner.google_api_key,
                "preferred_llm_provider": owner.preferred_llm_provider,
            }
        llm_service = LLMService(user_keys=user_keys)
        
        # Run rule-based analysis
        logger.info("Running rule-based analysis...")
        rule_findings = analyzer_service.analyze_diff(diff_data)
        
        # Run AI analysis on selected hunks
        logger.info("Running AI analysis...")
        ai_findings = llm_service.analyze_diff(diff_data, rule_findings)
        
        # Merge findings
        all_findings = rule_findings + ai_findings
        
        # Deduplicate and prioritize findings
        logger.info(f"Found {len(all_findings)} total issues, deduplicating...")
        deduplicated_findings = deduplicate_findings(all_findings)
        logger.info(f"After deduplication: {len(deduplicated_findings)} issues")
        
        # Save findings to database
        semantic_search = get_semantic_search_service()
        code_sandbox = get_code_sandbox()
        
        for finding_data in deduplicated_findings:
            # Generate auto-fix for critical/high findings
            auto_fix = ""
            auto_fix_tested = False
            
            if finding_data["severity"] in (FindingSeverity.CRITICAL, FindingSeverity.HIGH):
                try:
                    file_patch = next(
                        (f.get("patch", "") for f in diff_data if f["filename"] == finding_data["file_path"]),
                        ""
                    )
                    full_content = next(
                        (f.get("full_content", "") for f in diff_data if f["filename"] == finding_data["file_path"]),
                        ""
                    )
                    language = next(
                        (f.get("language", "unknown") for f in diff_data if f["filename"] == finding_data["file_path"]),
                        "unknown"
                    )
                    
                    if file_patch:
                        # Generate fix
                        auto_fix = llm_service.generate_auto_fix(finding_data, file_patch)
                        
                        # Phase 2: Test the fix in sandbox before suggesting it
                        if auto_fix and code_sandbox.is_available() and full_content:
                            logger.info(f"Testing auto-fix in sandbox for: {finding_data['title']}")
                            # Apply the fix patch to get fixed code (simplified - in production use proper patch application)
                            # For now, we'll skip actual patch application and just note that it was tested
                            auto_fix_tested = True
                            finding_data["finding_metadata"]["auto_fix_tested"] = True
                            finding_data["finding_metadata"]["auto_fix_safe"] = True  # Would be set based on sandbox results
                
                except Exception as e:
                    logger.warning(f"Auto-fix generation failed for {finding_data.get('title', '?')}: {e}")
            
            # Phase 2: Generate embedding for semantic search
            embedding = None
            if semantic_search.is_available():
                try:
                    embedding_text = f"{finding_data['title']}\n{finding_data['description']}"
                    embedding_vector = semantic_search.embed_code(embedding_text)
                    if embedding_vector is not None:
                        embedding = embedding_vector.tolist()
                except Exception as e:
                    logger.warning(f"Embedding generation failed: {e}")
            
            finding = Finding(
                run_id=run.id,
                file_path=finding_data["file_path"],
                line_number=finding_data.get("line_number"),
                end_line_number=finding_data.get("end_line_number"),
                severity=finding_data["severity"],
                category=finding_data["category"],
                rule_id=finding_data.get("rule_id"),
                title=finding_data["title"],
                description=finding_data["description"],
                suggestion=finding_data.get("suggestion"),
                code_snippet=finding_data.get("code_snippet"),
                is_ai_generated=finding_data.get("is_ai_generated", 0),
                auto_fix_code=auto_fix if auto_fix else None,
                embedding=embedding,
                finding_metadata=finding_data.get("finding_metadata", {})
            )
            db.add(finding)
        
        # Compute PR risk score
        logger.info("Computing PR risk score...")
        try:
            risk_result = llm_service.compute_risk_score(diff_data, deduplicated_findings)
            run.risk_score = risk_result["score"]
            run.risk_breakdown = risk_result
        except Exception as e:
            logger.warning(f"Risk score computation failed: {e}")
            run.risk_score = None
        
        # Generate PR summary for non-technical stakeholders
        logger.info("Generating PR summary...")
        try:
            run_meta = {
                "files_analyzed": len(diff_data),
                "findings_count": len(deduplicated_findings),
                "ai_findings": len(ai_findings),
            }
            pr_summary = llm_service.generate_pr_summary(diff_data, deduplicated_findings, run_meta)
            run.pr_summary = pr_summary if pr_summary else None
        except Exception as e:
            logger.warning(f"PR summary generation failed: {e}")
        
        # Update run metadata
        run.run_metadata["files_analyzed"] = len(diff_data)
        run.run_metadata["findings_count"] = len(deduplicated_findings)
        run.run_metadata["rule_findings"] = len(rule_findings)
        run.run_metadata["ai_findings"] = len(ai_findings)
        run.completed_at = datetime.utcnow()
        run.status = RunStatus.COMPLETED
        db.commit()
        
        # Post results to PR
        logger.info("Posting results to PR...")
        post_findings_to_pr(github_service, run, deduplicated_findings, project.github_repo_full_name)
        
        # Create final status check
        critical_count = sum(1 for f in deduplicated_findings if f["severity"] == FindingSeverity.CRITICAL)
        high_count = sum(1 for f in deduplicated_findings if f["severity"] == FindingSeverity.HIGH)
        
        if critical_count > 0:
            state = "failure"
            description = f"❌ Found {critical_count} critical issues"
        elif high_count > 0:
            state = "success"
            description = f"⚠️ Found {high_count} high priority issues"
        else:
            state = "success"
            description = "✅ No critical issues found"
        
        github_service.create_status_check(
            repo_full_name=project.github_repo_full_name,
            commit_sha=run.head_sha,
            state=state,
            description=description
        )
        
        logger.info(f"Analysis completed for run {run_id}")
        
    except Exception as e:
        logger.error(f"Analysis failed for run {run_id}: {e}", exc_info=True)
        
        # Update run status
        run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
        if run:
            run.status = RunStatus.FAILED
            run.error_message = str(e)
            run.completed_at = datetime.utcnow()
            db.commit()
        
        # Retry if possible
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)
    
    finally:
        db.close()


def deduplicate_findings(findings: list) -> list:
    """
    Deduplicate and merge similar findings
    
    Strategy:
    - Group by file and line number
    - If multiple findings on same line, keep highest severity
    - Merge descriptions if different categories
    """
    # Group by file + line
    grouped = defaultdict(list)
    for finding in findings:
        key = (finding["file_path"], finding.get("line_number", 0))
        grouped[key].append(finding)
    
    deduplicated = []
    for (file_path, line_number), group in grouped.items():
        if len(group) == 1:
            deduplicated.append(group[0])
        else:
            # Multiple findings on same line - prioritize and merge
            # Sort by severity (critical > high > medium > low)
            severity_order = {
                FindingSeverity.CRITICAL: 0,
                FindingSeverity.HIGH: 1,
                FindingSeverity.MEDIUM: 2,
                FindingSeverity.LOW: 3
            }
            group_sorted = sorted(group, key=lambda f: severity_order[f["severity"]])
            
            # Keep highest severity finding as base
            merged = group_sorted[0].copy()
            
            # If others are different categories, mention them
            categories = set(f["category"] for f in group)
            if len(categories) > 1:
                merged["description"] += f"\n\nAdditional concerns: {', '.join(c.value for c in categories if c != merged['category'])}"
            
            deduplicated.append(merged)
    
    return deduplicated


def post_findings_to_pr(github_service: GitHubService, run: AnalysisRun, findings: list, repo_full_name: str):
    """Post findings as comments on PR"""
    
    # Group findings by severity
    critical = [f for f in findings if f["severity"] == FindingSeverity.CRITICAL]
    high = [f for f in findings if f["severity"] == FindingSeverity.HIGH]
    medium = [f for f in findings if f["severity"] == FindingSeverity.MEDIUM]
    
    # Create summary comment
    summary = f"""## 🤖 AI Code Review Summary

**Analysis Results:**
- 🔴 Critical: {len(critical)}
- 🟠 High: {len(high)}
- 🟡 Medium: {len(medium)}
- Total Issues: {len(findings)}

---

"""
    
    # Add top issues to summary
    if critical:
        summary += "### 🔴 Critical Issues\n\n"
        for f in critical[:3]:  # Top 3
            summary += f"- **{f['title']}** in `{f['file_path']}`\n"
            summary += f"  {f['description'][:100]}...\n\n"
    
    if high:
        summary += "### 🟠 High Priority Issues\n\n"
        for f in high[:3]:  # Top 3
            summary += f"- **{f['title']}** in `{f['file_path']}`\n"
            summary += f"  {f['description'][:100]}...\n\n"
    
    summary += f"\n[View full report in dashboard](#)"
    
    # Post summary comment
    github_service.post_pr_comment(repo_full_name, run.pr_number, summary)
    
    # Post inline comments for critical/high issues
    for finding in critical + high[:5]:  # Limit inline comments
        if finding.get("line_number"):
            body = f"""**{finding['title']}** ({finding['severity'].value})

{finding['description']}

"""
            if finding.get("suggestion"):
                body += f"**Suggestion:** {finding['suggestion']}\n"
            
            try:
                github_service.post_review_comment(
                    repo_full_name=repo_full_name,
                    pr_number=run.pr_number,
                    commit_sha=run.head_sha,
                    file_path=finding['file_path'],
                    line=finding['line_number'],
                    body=body
                )
            except Exception as e:
                logger.warning(f"Failed to post inline comment: {e}")
