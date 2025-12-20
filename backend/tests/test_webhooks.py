"""
Webhook testing utilities and simulations
"""
import hmac
import hashlib
import json
from typing import Dict
from fastapi.testclient import TestClient
from app.config import settings


class WebhookTester:
    """Utility class for testing GitHub webhooks"""
    
    def __init__(self, client: TestClient):
        self.client = client
        self.webhook_secret = settings.github_webhook_secret
    
    def generate_signature(self, payload: Dict) -> str:
        """Generate GitHub webhook signature"""
        payload_str = json.dumps(payload)
        signature = hmac.new(
            self.webhook_secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    def send_webhook(self, event: str, payload: Dict) -> Dict:
        """Send a webhook event to the API"""
        headers = {
            "X-GitHub-Event": event,
            "X-Hub-Signature-256": self.generate_signature(payload),
            "Content-Type": "application/json"
        }
        
        response = self.client.post(
            "/api/webhooks/github",
            json=payload,
            headers=headers
        )
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code < 500 else None
        }
    
    def simulate_pr_opened(self, pr_number: int = 101, repo: str = "test-org/test-repo"):
        """Simulate PR opened event"""
        payload = {
            "action": "opened",
            "number": pr_number,
            "pull_request": {
                "id": 12345,
                "number": pr_number,
                "title": "Test PR",
                "user": {"login": "developer"},
                "html_url": f"https://github.com/{repo}/pull/{pr_number}",
                "base": {"sha": "abc123", "ref": "main"},
                "head": {"sha": "def456", "ref": "feature"}
            },
            "repository": {
                "full_name": repo,
                "name": repo.split("/")[1]
            },
            "installation": {"id": 11111111}
        }
        return self.send_webhook("pull_request", payload)
    
    def simulate_pr_synchronize(self, pr_number: int = 101):
        """Simulate PR synchronized (new commits) event"""
        payload = {
            "action": "synchronize",
            "number": pr_number,
            "pull_request": {
                "id": 12345,
                "number": pr_number,
                "head": {"sha": "new789"}
            },
            "repository": {"full_name": "test-org/test-repo"},
            "installation": {"id": 11111111}
        }
        return self.send_webhook("pull_request", payload)
    
    def simulate_pr_closed(self, pr_number: int = 101, merged: bool = True):
        """Simulate PR closed event"""
        payload = {
            "action": "closed",
            "number": pr_number,
            "pull_request": {
                "id": 12345,
                "number": pr_number,
                "merged": merged
            },
            "repository": {"full_name": "test-org/test-repo"},
            "installation": {"id": 11111111}
        }
        return self.send_webhook("pull_request", payload)


def test_webhook_signature_validation():
    """Test webhook signature validation"""
    from app.main import app
    client = TestClient(app)
    tester = WebhookTester(client)
    
    # Valid signature
    result = tester.simulate_pr_opened()
    assert result["status_code"] in [200, 202], f"Expected 200/202, got {result['status_code']}"
    
    # Invalid signature (manual request)
    response = client.post(
        "/api/webhooks/github",
        json={"action": "opened"},
        headers={
            "X-GitHub-Event": "pull_request",
            "X-Hub-Signature-256": "sha256=invalid_signature"
        }
    )
    assert response.status_code in [401, 403], "Invalid signature should be rejected"


def test_webhook_pr_lifecycle():
    """Test complete PR lifecycle via webhooks"""
    from app.main import app
    client = TestClient(app)
    tester = WebhookTester(client)
    
    # 1. PR opened
    result = tester.simulate_pr_opened(pr_number=999)
    assert result["status_code"] in [200, 202], "PR opened webhook should succeed"
    
    # 2. PR synchronized (new commits)
    result = tester.simulate_pr_synchronize(pr_number=999)
    assert result["status_code"] in [200, 202], "PR synchronize webhook should succeed"
    
    # 3. PR closed
    result = tester.simulate_pr_closed(pr_number=999, merged=True)
    assert result["status_code"] in [200, 202], "PR closed webhook should succeed"


if __name__ == "__main__":
    # Run webhook tests
    print("Testing webhook signature validation...")
    test_webhook_signature_validation()
    print("✓ Signature validation test passed")
    
    print("\nTesting PR lifecycle...")
    test_webhook_pr_lifecycle()
    print("✓ PR lifecycle test passed")
    
    print("\n✅ All webhook tests passed!")
