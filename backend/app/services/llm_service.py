from app.config import settings
from app.models import FindingSeverity, FindingCategory
import openai
import logging
import json
import requests

logger = logging.getLogger(__name__)


class LLMService:
    """Service for AI-powered code analysis using LLMs"""
    
    def __init__(self):
        self.use_openai = bool(settings.openai_api_key)
        self.use_anthropic = bool(settings.anthropic_api_key)
        self.use_google = bool(settings.google_api_key)
        self.provider = settings.llm_provider.lower()
        
        if self.use_openai:
            openai.api_key = settings.openai_api_key
    
    def analyze_diff(self, diff_data: list, rule_findings: list) -> list:
        """Analyze diff using LLM for complex reasoning"""
        findings = []
        
        # Filter files to analyze (focus on significant changes)
        files_to_analyze = [
            f for f in diff_data
            if f.get("patch") and f["additions"] + f["deletions"] > 5
        ][:10]  # Limit to 10 files
        
        for file_data in files_to_analyze:
            try:
                file_findings = self._analyze_file_with_llm(file_data, rule_findings)
                findings.extend(file_findings)
            except Exception as e:
                logger.error(f"LLM analysis failed for {file_data['filename']}: {e}")
        
        return findings
    
    def _analyze_file_with_llm(self, file_data: dict, rule_findings: list) -> list:
        """Analyze a single file with LLM"""
        filename = file_data["filename"]
        patch = file_data.get("patch", "")
        
        # Limit patch size
        if len(patch) > settings.max_lines_per_llm_call * 100:
            patch = patch[:settings.max_lines_per_llm_call * 100]
        
        # Build prompt
        prompt = self._build_analysis_prompt(filename, patch, rule_findings)
        
        # Call LLM
        if self.provider == "google" and self.use_google:
            response = self._call_google(prompt)
        elif self.use_openai:
            response = self._call_openai(prompt)
        else:
            # Fallback: return empty if no LLM configured
            return []
        
        # Parse response
        findings = self._parse_llm_response(response, filename)
        
        return findings
    
    def _build_analysis_prompt(self, filename: str, patch: str, rule_findings: list) -> str:
        """Build prompt for LLM analysis with few-shot examples"""
        prompt = f"""You are an expert code reviewer with deep knowledge of software engineering best practices, security vulnerabilities, and performance optimization.

File: {filename}

Code Diff:
```
{patch}
```

**Analysis Objectives:**
1. **Logic & Correctness**: Identify bugs, incorrect logic, edge cases, off-by-one errors
2. **Security**: Find vulnerabilities beyond simple patterns (auth bypasses, race conditions, TOCTOU, etc.)
3. **Performance**: Detect inefficient algorithms, N+1 queries, memory leaks, unnecessary computations
4. **Concurrency**: Identify race conditions, deadlock risks, thread-safety issues
5. **Error Handling**: Gaps in error recovery, unhandled edge cases, resource leaks
6. **Maintainability**: Complex code, poor naming, missing documentation for complex logic

**Context:**
- Rule-based static analysis already detected {len([f for f in rule_findings if f['file_path'] == filename])} issues
- Focus on issues that require reasoning and context understanding
- Ignore trivial style issues already caught by linters

**Example Quality Findings:**

```json
[
  {{
    "line_number": 15,
    "severity": "high",
    "category": "bug",
    "title": "Race condition in concurrent access",
    "description": "The counter variable is accessed by multiple threads without synchronization. Two threads could read the same value simultaneously, increment it, and write back, resulting in lost updates.",
    "suggestion": "Use threading.Lock() or atomic operations (threading.local, queue.Queue) to protect the counter variable."
  }},
  {{
    "line_number": 42,
    "severity": "medium",
    "category": "performance",
    "title": "N+1 query in loop",
    "description": "The code fetches user details inside a loop for each post, resulting in N+1 database queries. For 1000 posts, this would execute 1001 queries.",
    "suggestion": "Use select_related() or prefetch_related() to fetch users in a single query, or restructure to use a JOIN."
  }},
  {{
    "line_number": 67,
    "severity": "critical",
    "category": "security",
    "title": "Time-of-check to time-of-use (TOCTOU) vulnerability",
    "description": "The code checks if file exists, then opens it later. An attacker could replace the file with a symlink to sensitive data between the check and use.",
    "suggestion": "Open the file once with error handling, or use os.open() with O_EXCL|O_CREAT to prevent TOCTOU attacks."
  }}
]
```

**Output Format:**
Return a valid JSON array of findings. Each finding must have:
- line_number: Integer (use best estimate from diff context)
- severity: One of ["critical", "high", "medium", "low"]
- category: One of ["bug", "security", "performance", "best_practice"]
- title: String (concise, under 80 chars)
- description: String (detailed explanation with impact)
- suggestion: String (specific, actionable fix)

**Guidelines:**
- Only report significant issues (not cosmetic)
- Be specific with line numbers based on the diff
- Include WHY it's a problem, not just WHAT
- Provide actionable suggestions
- If no issues found, return: []
- Return ONLY the JSON array, no markdown formatting

Your JSON response:
"""
        return prompt
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API with retry logic"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = openai.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are an expert code reviewer specializing in security, performance, and correctness. Respond only with valid JSON arrays."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,  # Lower for more consistent output
                    max_tokens=2000,
                    response_format={"type": "json_object"} if retry_count > 0 else None  # Force JSON on retry
                )
                return response.choices[0].message.content
            except openai.RateLimitError:
                logger.warning(f"Rate limit hit, retry {retry_count + 1}/{max_retries}")
                retry_count += 1
                if retry_count < max_retries:
                    import time
                    time.sleep(2 ** retry_count)  # Exponential backoff
                else:
                    raise
            except Exception as e:
                logger.error(f"OpenAI API error: {e}")
                raise
    
    def _call_google(self, prompt: str) -> str:
        """Call Google Gemini API"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.google_api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 2000,
                    "responseMimeType": "application/json"
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text
            else:
                logger.warning("No content in Gemini response")
                return "[]"
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Google Gemini API error: {e}")
            return "[]"
        except Exception as e:
            logger.error(f"Error calling Google Gemini: {e}")
            return "[]"
    
    def _parse_llm_response(self, response: str, filename: str) -> list:
        """Parse LLM response into findings with robust error handling"""
        findings = []
        
        try:
            # Try to extract JSON from response (handle markdown code blocks)
            response_clean = response.strip()
            
            # Remove markdown code blocks if present
            if response_clean.startswith('```'):
                lines = response_clean.split('\n')
                response_clean = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_clean
            
            # Find JSON array
            json_start = response_clean.find('[')
            json_end = response_clean.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No JSON array found in LLM response")
                return []
            
            json_str = response_clean[json_start:json_end]
            data = json.loads(json_str)
            
            # Validate it's a list
            if not isinstance(data, list):
                logger.warning(f"LLM response is not a list: {type(data)}")
                return []
            
            # Map severity
            severity_map = {
                "critical": FindingSeverity.CRITICAL,
                "high": FindingSeverity.HIGH,
                "medium": FindingSeverity.MEDIUM,
                "low": FindingSeverity.LOW
            }
            
            # Map category
            category_map = {
                "bug": FindingCategory.BUG,
                "security": FindingCategory.SECURITY,
                "performance": FindingCategory.PERFORMANCE,
                "best_practice": FindingCategory.BEST_PRACTICE
            }
            
            for idx, item in enumerate(data):
                # Validate required fields
                if not isinstance(item, dict):
                    logger.warning(f"Skipping invalid finding {idx}: not a dict")
                    continue
                
                if not item.get("title") or not item.get("description"):
                    logger.warning(f"Skipping finding {idx}: missing title or description")
                    continue
                
                finding = {
                    "file_path": filename,
                    "line_number": item.get("line_number", 0),
                    "severity": severity_map.get(item.get("severity", "").lower(), FindingSeverity.MEDIUM),
                    "category": category_map.get(item.get("category", "").lower(), FindingCategory.BUG),
                    "rule_id": "AI:reasoning",
                    "title": item.get("title", "AI-detected issue")[:200],  # Limit length
                    "description": item.get("description", "")[:1000],
                    "suggestion": item.get("suggestion", "")[:500],
                    "is_ai_generated": 1,
                    "finding_metadata": {"source": "llm", "model": "gpt-4-turbo-preview"}
                }
                findings.append(finding)
            
            logger.info(f"Parsed {len(findings)} findings from LLM response")
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}\nResponse: {response[:200]}")
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}")
        
        return findings
