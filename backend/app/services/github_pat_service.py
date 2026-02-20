"""
GitHub PAT (Personal Access Token) Service.

SaaS-oriented GitHub service that uses a user's Personal Access Token
instead of a GitHub App installation. Each user provides their own PAT
in their account settings.
"""

import logging
import secrets

logger = logging.getLogger(__name__)

try:
    from github import Github, GithubException
    HAS_PYGITHUB = True
except ImportError:
    Github = None  # type: ignore
    GithubException = Exception  # type: ignore
    HAS_PYGITHUB = False
    logger.debug("PyGithub not installed; GitHub PAT features unavailable")


class GitHubPATService:
    """GitHub service using Personal Access Tokens (SaaS model)."""

    def __init__(self, token: str):
        if not HAS_PYGITHUB:
            raise RuntimeError("PyGithub package is not installed")
        if not token:
            raise ValueError("GitHub Personal Access Token is required")
        self._token = token
        self._client = Github(token)

    @property
    def client(self) -> Github:
        return self._client

    def validate_token(self) -> dict:
        """Validate the PAT and return user info."""
        try:
            user = self._client.get_user()
            return {
                "valid": True,
                "login": user.login,
                "name": user.name,
                "avatar_url": user.avatar_url,
                "scopes": list(self._client.oauth_scopes or []),
            }
        except GithubException as e:
            logger.warning(f"GitHub token validation failed: {e}")
            return {"valid": False, "error": str(e)}

    def validate_repo_access(self, repo_full_name: str) -> dict:
        """Check if the token has access to a specific repo."""
        try:
            repo = self._client.get_repo(repo_full_name)
            return {
                "accessible": True,
                "full_name": repo.full_name,
                "private": repo.private,
                "default_branch": repo.default_branch,
                "permissions": {
                    "admin": repo.permissions.admin if repo.permissions else False,
                    "push": repo.permissions.push if repo.permissions else False,
                    "pull": repo.permissions.pull if repo.permissions else False,
                },
            }
        except GithubException as e:
            logger.warning(f"Repo access check failed for {repo_full_name}: {e}")
            return {"accessible": False, "error": str(e)}

    def get_pr_diff(self, repo_full_name: str, pr_number: int, include_full_content: bool = True) -> list:
        """Get PR diff data (list of file changes).
        
        Args:
            repo_full_name: Repository full name (owner/repo)
            pr_number: Pull request number
            include_full_content: If True, fetches full file content for context (default: True)
        
        Returns:
            List of file change dictionaries with optional full content
        """
        repo = self._client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)

        diff_data = []
        for file in pr.get_files():
            file_data = {
                "filename": file.filename,
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "patch": file.patch if hasattr(file, "patch") else None,
            }
            
            # Fetch full file content for better context
            if include_full_content and file.status != "removed":
                try:
                    content = self.get_file_content(repo_full_name, file.filename, pr.head.sha)
                    file_data["full_content"] = content
                    file_data["language"] = self._detect_language(file.filename)
                except Exception as e:
                    logger.warning(f"Failed to fetch full content for {file.filename}: {e}")
                    file_data["full_content"] = None
            
            diff_data.append(file_data)

        return diff_data

    def get_file_content(self, repo_full_name: str, file_path: str, ref: str = "main") -> str:
        """Fetch the full content of a file from a repository.
        
        Args:
            repo_full_name: Repository full name (owner/repo)
            file_path: Path to the file in the repository
            ref: Git reference (branch, tag, or commit SHA)
        
        Returns:
            File content as string
        """
        try:
            repo = self._client.get_repo(repo_full_name)
            file_content = repo.get_contents(file_path, ref=ref)
            
            if isinstance(file_content, list):
                # It's a directory, not a file
                return ""
                
            # Decode base64 content
            import base64
            content = base64.b64decode(file_content.content).decode("utf-8")
            return content
        except Exception as e:
            logger.error(f"Failed to fetch {file_path} at {ref}: {e}")
            return ""

    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename extension."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sql": "sql",
            ".sh": "bash",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".json": "json",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".md": "markdown",
        }
        
        for ext, lang in ext_map.items():
            if filename.endswith(ext):
                return lang
        
        return "unknown"

    def get_pr_info(self, repo_full_name: str, pr_number: int) -> dict:
        """Get PR metadata."""
        repo = self._client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)

        return {
            "pr_number": pr.number,
            "pr_url": pr.html_url,
            "pr_title": pr.title,
            "pr_author": pr.user.login if pr.user else "unknown",
            "base_sha": pr.base.sha,
            "head_sha": pr.head.sha,
            "state": pr.state,
            "repo_full_name": repo.full_name,
        }

    def get_pr_files(self, repo_full_name: str, pr_number: int) -> list:
        """Get list of files changed in PR."""
        repo = self._client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)

        return [
            {
                "filename": f.filename,
                "status": f.status,
                "additions": f.additions,
                "deletions": f.deletions,
            }
            for f in pr.get_files()
        ]

    def list_open_prs(self, repo_full_name: str, limit: int = 20) -> list:
        """List open PRs for a repo."""
        repo = self._client.get_repo(repo_full_name)
        prs = repo.get_pulls(state="open", sort="updated", direction="desc")

        result = []
        for pr in prs[:limit]:
            result.append({
                "number": pr.number,
                "title": pr.title,
                "author": pr.user.login if pr.user else "unknown",
                "url": pr.html_url,
                "created_at": pr.created_at.isoformat() if pr.created_at else None,
                "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
                "head_sha": pr.head.sha,
                "base_sha": pr.base.sha,
            })
        return result

    def post_pr_comment(self, repo_full_name: str, pr_number: int, body: str):
        """Post a comment on a PR."""
        repo = self._client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        pr.create_issue_comment(body)
        logger.info(f"Posted comment on PR #{pr_number}")

    def post_review_comment(
        self,
        repo_full_name: str,
        pr_number: int,
        commit_sha: str,
        file_path: str,
        line: int,
        body: str,
    ):
        """Post an inline review comment on a specific line."""
        repo = self._client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)

        try:
            pr.create_review_comment(
                body=body,
                commit=repo.get_commit(commit_sha),
                path=file_path,
                line=line,
            )
            logger.info(f"Posted review comment on {file_path}:{line}")
        except Exception as e:
            logger.error(f"Failed to post review comment: {e}")

    def create_status_check(
        self,
        repo_full_name: str,
        commit_sha: str,
        state: str,
        description: str,
        context: str = "CodeLens AI Review",
    ):
        """Create a status check on a commit."""
        try:
            repo = self._client.get_repo(repo_full_name)
            commit = repo.get_commit(commit_sha)
            commit.create_status(
                state=state,
                description=description,
                context=context,
            )
            logger.info(f"Created status check: {state} - {description}")
        except Exception as e:
            logger.warning(f"Failed to create status check (may lack permissions): {e}")

    def setup_webhook(self, repo_full_name: str, webhook_url: str, secret: str) -> dict:
        """Create a webhook on a repo (requires admin access)."""
        try:
            repo = self._client.get_repo(repo_full_name)
            hook = repo.create_hook(
                name="web",
                config={
                    "url": webhook_url,
                    "content_type": "json",
                    "secret": secret,
                    "insecure_ssl": "0",
                },
                events=["pull_request"],
                active=True,
            )
            return {
                "success": True,
                "hook_id": hook.id,
                "url": webhook_url,
            }
        except GithubException as e:
            logger.error(f"Failed to create webhook for {repo_full_name}: {e}")
            return {"success": False, "error": str(e)}


def generate_webhook_secret() -> str:
    """Generate a secure random webhook secret."""
    return secrets.token_hex(32)
