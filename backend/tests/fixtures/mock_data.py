"""
Mock data and fixtures for testing
"""
from datetime import datetime, timedelta


# Mock PR data
MOCK_PR_DATA = {
    "pr_with_security_issues": {
        "number": 101,
        "title": "Add user authentication",
        "author": "developer1",
        "url": "https://github.com/test-org/test-repo/pull/101",
        "base_sha": "abc123def456",
        "head_sha": "xyz789uvw012",
        "diff": """diff --git a/app/auth.py b/app/auth.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/app/auth.py
@@ -0,0 +1,25 @@
+import pickle
+import hashlib
+
+def authenticate_user(username, password):
+    # Security issue: hardcoded credentials
+    API_KEY = "sk-1234567890abcdef"
+    
+    # Security issue: weak hashing
+    password_hash = hashlib.md5(password.encode()).hexdigest()
+    
+    # Security issue: SQL injection
+    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password_hash}'"
+    
+    return execute_query(query)
+
+def load_user_data(data):
+    # Security issue: unsafe deserialization
+    user = pickle.loads(data)
+    return user
+
+def execute_command(cmd):
+    # Security issue: command injection
+    import os
+    os.system(f"ls {cmd}")
+    return "Done"
""",
        "files": ["app/auth.py"],
        "expected_findings": [
            "security.hardcoded_secrets",
            "security.weak_cryptography",
            "security.sql_injection",
            "security.unsafe_deserialization",
            "security.command_injection"
        ]
    },
    
    "pr_with_code_quality_issues": {
        "number": 102,
        "title": "Add data processing function",
        "author": "developer2",
        "url": "https://github.com/test-org/test-repo/pull/102",
        "base_sha": "def456ghi789",
        "head_sha": "uvw012rst345",
        "diff": """diff --git a/app/processor.py b/app/processor.py
new file mode 100644
index 0000000..7654321
--- /dev/null
+++ b/app/processor.py
@@ -0,0 +1,30 @@
+def process_data(items):
+    # Code quality issue: missing error handling
+    result = []
+    
+    # Code quality issue: magic numbers
+    for item in items:
+        if item > 100:
+            value = item * 0.85
+        else:
+            value = item * 1.15
+        result.append(value)
+    
+    # Code quality issue: console logging
+    print(f"Processed {len(result)} items")
+    
+    return result
+
+def calculate_total(data):
+    # Code quality issue: long function, deep nesting
+    total = 0
+    for category in data:
+        if category['active']:
+            for item in category['items']:
+                if item['valid']:
+                    for price in item['prices']:
+                        if price['currency'] == 'USD':
+                            if price['amount'] > 0:
+                                total += price['amount']
+    return total
""",
        "files": ["app/processor.py"],
        "expected_findings": [
            "quality.missing_error_handling",
            "quality.magic_numbers",
            "quality.console_log",
            "quality.long_function",
            "quality.deep_nesting"
        ]
    },
    
    "pr_with_performance_issues": {
        "number": 103,
        "title": "Optimize database queries",
        "author": "developer3",
        "url": "https://github.com/test-org/test-repo/pull/103",
        "base_sha": "ghi789jkl012",
        "head_sha": "rst345vwx678",
        "diff": """diff --git a/app/database.py b/app/database.py
new file mode 100644
index 0000000..9876543
--- /dev/null
+++ b/app/database.py
@@ -0,0 +1,20 @@
+def get_user_posts(user_ids):
+    # Performance issue: N+1 query
+    posts = []
+    for user_id in user_ids:
+        user = db.query(User).filter(User.id == user_id).first()
+        user_posts = db.query(Post).filter(Post.user_id == user_id).all()
+        posts.extend(user_posts)
+    return posts
+
+def filter_items(items):
+    # Performance issue: inefficient loop
+    result = []
+    for item in items:
+        if item not in result:
+            result.append(item)
+    return result
+
+var data = []
+function addData(item) {
+    // Performance issue: memory leak (missing cleanup)
+    data.push(item)
+}
""",
        "files": ["app/database.py"],
        "expected_findings": [
            "performance.n_plus_one_query",
            "performance.inefficient_loop"
        ]
    },
    
    "pr_clean_code": {
        "number": 104,
        "title": "Add well-written utility functions",
        "author": "developer4",
        "url": "https://github.com/test-org/test-repo/pull/104",
        "base_sha": "jkl012mno345",
        "head_sha": "vwx678yz9012",
        "diff": """diff --git a/app/utils.py b/app/utils.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/app/utils.py
@@ -0,0 +1,20 @@
+from typing import List, Optional
+
+def calculate_average(numbers: List[float]) -> Optional[float]:
+    \"\"\"
+    Calculate the average of a list of numbers.
+    
+    Args:
+        numbers: List of numbers to average
+        
+    Returns:
+        Average value or None if list is empty
+    \"\"\"
+    if not numbers:
+        return None
+    
+    try:
+        return sum(numbers) / len(numbers)
+    except (TypeError, ZeroDivisionError) as e:
+        logger.error(f"Error calculating average: {e}")
+        return None
""",
        "files": ["app/utils.py"],
        "expected_findings": []
    }
}


# Mock webhook payloads
MOCK_WEBHOOK_PAYLOADS = {
    "pull_request_opened": {
        "action": "opened",
        "number": 101,
        "pull_request": {
            "id": 12345,
            "number": 101,
            "title": "Add user authentication",
            "user": {
                "login": "developer1"
            },
            "html_url": "https://github.com/test-org/test-repo/pull/101",
            "base": {
                "sha": "abc123def456",
                "ref": "main"
            },
            "head": {
                "sha": "xyz789uvw012",
                "ref": "feature/auth"
            }
        },
        "repository": {
            "id": 98765,
            "full_name": "test-org/test-repo",
            "name": "test-repo",
            "owner": {
                "login": "test-org"
            }
        },
        "installation": {
            "id": 11111111
        }
    },
    
    "pull_request_synchronize": {
        "action": "synchronize",
        "number": 101,
        "pull_request": {
            "id": 12345,
            "number": 101,
            "title": "Add user authentication",
            "user": {
                "login": "developer1"
            },
            "html_url": "https://github.com/test-org/test-repo/pull/101",
            "base": {
                "sha": "abc123def456",
                "ref": "main"
            },
            "head": {
                "sha": "new789xyz012",
                "ref": "feature/auth"
            }
        },
        "repository": {
            "id": 98765,
            "full_name": "test-org/test-repo",
            "name": "test-repo"
        },
        "installation": {
            "id": 11111111
        }
    },
    
    "pull_request_closed": {
        "action": "closed",
        "number": 101,
        "pull_request": {
            "id": 12345,
            "number": 101,
            "merged": True
        },
        "repository": {
            "full_name": "test-org/test-repo"
        },
        "installation": {
            "id": 11111111
        }
    }
}


# Mock GitHub API responses
MOCK_GITHUB_RESPONSES = {
    "get_pr_diff": MOCK_PR_DATA["pr_with_security_issues"]["diff"],
    "get_pr_files": [
        {
            "filename": "app/auth.py",
            "status": "added",
            "additions": 25,
            "deletions": 0,
            "changes": 25,
            "patch": MOCK_PR_DATA["pr_with_security_issues"]["diff"]
        }
    ],
    "create_status": {
        "state": "success",
        "description": "Code review completed",
        "context": "ai-code-review"
    },
    "create_review": {
        "id": 54321,
        "body": "Automated code review completed"
    }
}


# Expected analysis results
EXPECTED_ANALYSIS_RESULTS = {
    "pr_with_security_issues": {
        "total_findings": 5,
        "critical_findings": 3,
        "high_findings": 2,
        "categories": {
            "security": 5
        },
        "files_analyzed": 1
    },
    "pr_with_code_quality_issues": {
        "total_findings": 5,
        "critical_findings": 0,
        "high_findings": 0,
        "medium_findings": 3,
        "low_findings": 2,
        "categories": {
            "style": 2,
            "best_practice": 3
        },
        "files_analyzed": 1
    },
    "pr_with_performance_issues": {
        "total_findings": 2,
        "high_findings": 1,
        "medium_findings": 1,
        "categories": {
            "performance": 2
        },
        "files_analyzed": 1
    },
    "pr_clean_code": {
        "total_findings": 0,
        "files_analyzed": 1
    }
}
