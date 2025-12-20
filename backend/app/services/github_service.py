import hmac
import hashlib
import jwt
import time
from github import Github, GithubIntegration
from app.config import settings
import logging

logger = logging.getLogger(__name__)


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
    
    def _get_installation_token(self) -> str:
        """Generate installation access token"""
        with open(settings.github_app_private_key_path, 'r') as key_file:
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
    
    def get_pr_diff(self, repo_full_name: str, pr_number: int) -> str:
        """Get PR diff"""
        repo = self.client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        
        # Get diff
        files = pr.get_files()
        diff_data = []
        
        for file in files:
            diff_data.append({
                "filename": file.filename,
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "patch": file.patch if hasattr(file, 'patch') else None
            })
        
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
