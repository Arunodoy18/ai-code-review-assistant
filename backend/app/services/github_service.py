import hmac
import hashlib
import time
from pathlib import Path

from app.config import settings

import logging

logger = logging.getLogger(__name__)

try:
    import jwt
except ImportError:
    jwt = None  # type: ignore
    logger.info("PyJWT not installed; GitHub App JWT auth unavailable")

try:
    from github import Github, GithubIntegration
except ImportError:
    Github = None  # type: ignore
    GithubIntegration = None  # type: ignore
    logger.info("PyGithub not installed; GitHub API integration unavailable")


def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify GitHub webhook signature"""
    if not signature_header:
        return False
    
    hash_object = hmac.new(
        settings.github_webhook_secret.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)


def parse_pr_event(payload: dict) -> dict:
    """Parse PR event payload and extract relevant data"""
    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})
    
    return {
        "pr_number": pr.get("number"),
        "pr_url": pr.get("html_url"),
        "pr_title": pr.get("title"),
        "pr_author": pr.get("user", {}).get("login"),
        "base_sha": pr.get("base", {}).get("sha"),
        "head_sha": pr.get("head", {}).get("sha"),
        "repo_name": repo.get("name"),
        "repo_full_name": repo.get("full_name"),
        "repo_owner": repo.get("owner", {}).get("login"),
    }


class GitHubService:
    """Service for interacting with GitHub API"""
    
    def __init__(self, installation_id: int):
        self.installation_id = installation_id
        self._github_client = None
        if not settings.enable_github_integration:
            raise RuntimeError("GitHub integration is disabled in this environment")
        private_key_path = settings.resolve_github_private_key_path()
        if not private_key_path:
            raise RuntimeError("GitHub App private key is not configured")
        if not Path(private_key_path).exists():
            raise RuntimeError(f"GitHub App private key not found at {private_key_path}")
        self._private_key_path = private_key_path
    
    def _get_installation_token(self) -> str:
        """Generate installation access token"""
        with open(self._private_key_path, 'r', encoding='utf-8') as key_file:
            private_key = key_file.read()
        
        # Create JWT
        payload = {
            'iat': int(time.time()),
            'exp': int(time.time()) + 600,  # 10 minutes
            'iss': settings.github_app_id
        }
        
        jwt_token = jwt.encode(payload, private_key, algorithm='RS256')
        
        # Get installation token
        integration = GithubIntegration(settings.github_app_id, private_key)
        auth = integration.get_access_token(self.installation_id)
        
        return auth.token
    
    @property
    def client(self) -> Github:
        """Get authenticated GitHub client"""
        if not self._github_client:
            token = self._get_installation_token()
            self._github_client = Github(token)
        return self._github_client
    
    def get_pr_diff(self, repo_full_name: str, pr_number: int, include_full_content: bool = True) -> str:
        """Get PR diff with optional full file content.
        
        Args:
            repo_full_name: Repository full name (owner/repo)
            pr_number: Pull request number
            include_full_content: If True, fetch full file content for each changed file
        
        Returns:
            List of file diffs with optional full content
        """
        repo = self.client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        
        # Get diff
        files = pr.get_files()
        diff_data = []
        
        for file in files:
            file_info = {
                "filename": file.filename,
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "patch": file.patch if hasattr(file, 'patch') else None
            }
            
            # Optionally fetch full file content for better context
            if include_full_content and file.status != "removed":
                try:
                    full_content = self.get_file_content(repo_full_name, file.filename, pr.head.sha)
                    file_info["full_content"] = full_content
                    file_info["language"] = self._detect_language(file.filename)
                except Exception as e:
                    logger.warning(f"Could not fetch full content for {file.filename}: {e}")
                    file_info["full_content"] = None
                    file_info["language"] = self._detect_language(file.filename)
            
            diff_data.append(file_info)
        
        return diff_data
    
    def get_pr_files(self, repo_full_name: str, pr_number: int) -> list:
        """Get list of files changed in PR"""
        repo = self.client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        files = pr.get_files()
        
        return [
            {
                "filename": f.filename,
                "status": f.status,
                "additions": f.additions,
                "deletions": f.deletions
            }
            for f in files
        ]
    
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
            repo = self.client.get_repo(repo_full_name)
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
    
    def post_pr_comment(self, repo_full_name: str, pr_number: int, body: str):
        """Post a comment on PR"""
        repo = self.client.get_repo(repo_full_name)
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
        body: str
    ):
        """Post an inline review comment on specific line"""
        repo = self.client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        
        try:
            pr.create_review_comment(
                body=body,
                commit=repo.get_commit(commit_sha),
                path=file_path,
                line=line
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
        context: str = "AI Code Review"
    ):
        """Create a status check on commit"""
        repo = self.client.get_repo(repo_full_name)
        commit = repo.get_commit(commit_sha)
        
        commit.create_status(
            state=state,  # pending, success, failure, error
            description=description,
            context=context
        )
        logger.info(f"Created status check: {state} - {description}")
