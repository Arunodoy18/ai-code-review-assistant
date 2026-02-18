from app.config import settings
from app.models import FindingSeverity, FindingCategory
import openai
import logging
import json
import requests

logger = logging.getLogger(__name__)

try:
    import anthropic as anthropic_sdk
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    logger.info("anthropic package not installed; Anthropic provider unavailable")


class LLMService:
    """Service for AI-powered code analysis using LLMs"""
    
    def __init__(self):
        self.use_openai = bool(settings.openai_api_key)
        self.use_anthropic = bool(settings.anthropic_api_key) and HAS_ANTHROPIC
        self.use_google = bool(settings.google_api_key)
        self.use_groq = bool(settings.groq_api_key)
        self.provider = settings.llm_provider.lower()
        
        if self.use_openai:
            openai.api_key = settings.openai_api_key
        
        if self.use_anthropic:
            self.anthropic_client = anthropic_sdk.Anthropic(api_key=settings.anthropic_api_key)
        
        if self.use_groq:
            self.groq_client = openai.OpenAI(
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
    
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
        
        # Call LLM based on configured provider
        if self.provider == "groq" and self.use_groq:
            response = self._call_groq(prompt)
        elif self.provider == "anthropic" and self.use_anthropic:
            response = self._call_anthropic(prompt)
        elif self.provider == "google" and self.use_google:
            response = self._call_google(prompt)
        elif self.use_groq:
            response = self._call_groq(prompt)
        elif self.use_openai:
            response = self._call_openai(prompt)
        elif self.use_anthropic:
            response = self._call_anthropic(prompt)
        elif self.use_google:
            response = self._call_google(prompt)
        else:
            # No LLM configured
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
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic Claude API with retry logic"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                message = self.anthropic_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2000,
                    temperature=0.2,
                    system="You are an expert code reviewer specializing in security, performance, and correctness. Respond only with valid JSON arrays.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                )
                # Extract text from the response
                text = message.content[0].text if message.content else "[]"
                return text
            except Exception as e:
                if "rate" in str(e).lower() or "overloaded" in str(e).lower():
                    logger.warning(f"Anthropic rate limit, retry {retry_count + 1}/{max_retries}")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(2 ** retry_count)
                    else:
                        raise
                else:
                    logger.error(f"Anthropic API error: {e}")
                    raise
    
    def _call_groq(self, prompt: str) -> str:
        """Call Groq API (OpenAI-compatible) with retry logic"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = self.groq_client.chat.completions.create(
                    model=settings.groq_model,
                    messages=[
                        {"role": "system", "content": "You are an expert code reviewer specializing in security, performance, and correctness. Respond only with valid JSON arrays."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=4000,
                )
                return response.choices[0].message.content
            except Exception as e:
                if "rate" in str(e).lower() or "limit" in str(e).lower():
                    logger.warning(f"Groq rate limit, retry {retry_count + 1}/{max_retries}")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(2 ** retry_count)
                    else:
                        raise
                else:
                    logger.error(f"Groq API error: {e}")
                    raise
    
    def _call_llm_raw(self, system_prompt: str, user_prompt: str) -> str:
        """Generic LLM call that returns raw text (not just JSON arrays).
        Used by risk score, auto-fix, and PR summary features."""
        if self.provider == "groq" and self.use_groq:
            return self._call_groq_raw(system_prompt, user_prompt)
        elif self.provider == "anthropic" and self.use_anthropic:
            msg = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514", max_tokens=4000, temperature=0.3,
                system=system_prompt, messages=[{"role": "user", "content": user_prompt}])
            return msg.content[0].text if msg.content else ""
        elif self.use_groq:
            return self._call_groq_raw(system_prompt, user_prompt)
        elif self.use_openai:
            resp = openai.chat.completions.create(
                model="gpt-4-turbo-preview", max_tokens=4000, temperature=0.3,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}])
            return resp.choices[0].message.content
        elif self.use_google:
            return self._call_google(f"{system_prompt}\n\n{user_prompt}")
        return ""
    
    def _call_groq_raw(self, system_prompt: str, user_prompt: str) -> str:
        """Call Groq with arbitrary system/user prompts"""
        response = self.groq_client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=4000,
        )
        return response.choices[0].message.content
    
    def compute_risk_score(self, diff_data: list, findings: list) -> dict:
        """Compute a 0-100 PR risk score using AI + heuristics.
        
        Returns: { score: float, label: str, breakdown: dict, explanation: str }
        """
        # Heuristic factors
        total_additions = sum(f.get("additions", 0) for f in diff_data)
        total_deletions = sum(f.get("deletions", 0) for f in diff_data)
        files_changed = len(diff_data)
        
        critical_count = sum(1 for f in findings if f.get("severity") in ("critical", FindingSeverity.CRITICAL))
        high_count = sum(1 for f in findings if f.get("severity") in ("high", FindingSeverity.HIGH))
        medium_count = sum(1 for f in findings if f.get("severity") in ("medium", FindingSeverity.MEDIUM))
        
        # Sensitive file patterns (high blast radius)
        sensitive_patterns = [
            "auth", "security", "password", "token", "key", "secret",
            "payment", "billing", "database", "migration", "config",
            ".env", "docker", "ci", "deploy", "infra"
        ]
        sensitive_files = sum(
            1 for f in diff_data
            if any(p in f.get("filename", "").lower() for p in sensitive_patterns)
        )
        
        # Compute heuristic score components
        size_score = min(30, (total_additions + total_deletions) / 20)  # 0-30
        severity_score = min(40, critical_count * 15 + high_count * 8 + medium_count * 3)  # 0-40
        blast_radius = min(15, files_changed * 1.5 + sensitive_files * 5)  # 0-15
        complexity_score = min(15, (total_additions / max(total_deletions, 1)) * 3 if total_deletions > 0 else 5)  # 0-15
        
        heuristic_score = round(min(100, size_score + severity_score + blast_radius + complexity_score))
        
        # AI refinement (ask LLM for context-aware adjustment)
        try:
            file_list = ", ".join(f.get("filename", "?") for f in diff_data[:15])
            finding_summary = "; ".join(
                f"{f.get('title', '?')} ({f.get('severity', '?')})" 
                for f in findings[:10]
            )
            
            ai_prompt = f"""Given this PR analysis, provide a risk assessment as JSON:
- Files changed ({files_changed}): {file_list}
- Lines: +{total_additions} -{total_deletions}
- Findings: {len(findings)} total ({critical_count} critical, {high_count} high, {medium_count} medium)
- Key findings: {finding_summary or 'None'}
- Sensitive files touched: {sensitive_files}

Return ONLY valid JSON: {{"ai_adjustment": <number -15 to +15>, "explanation": "<one paragraph why this PR is risky or safe>"}}"""
            
            ai_response = self._call_llm_raw(
                "You are a senior engineering manager assessing PR merge risk. Return JSON only.",
                ai_prompt
            )
            
            ai_data = json.loads(ai_response.strip().strip('```json').strip('```'))
            ai_adjustment = max(-15, min(15, ai_data.get("ai_adjustment", 0)))
            explanation = ai_data.get("explanation", "")
        except Exception as e:
            logger.warning(f"AI risk adjustment failed: {e}")
            ai_adjustment = 0
            explanation = ""
        
        final_score = round(max(0, min(100, heuristic_score + ai_adjustment)))
        
        if final_score >= 80:
            label = "critical"
        elif final_score >= 60:
            label = "high"
        elif final_score >= 35:
            label = "medium"
        else:
            label = "low"
        
        return {
            "score": final_score,
            "label": label,
            "explanation": explanation,
            "breakdown": {
                "size_impact": round(size_score),
                "severity_impact": round(severity_score),
                "blast_radius": round(blast_radius),
                "complexity": round(complexity_score),
                "ai_adjustment": ai_adjustment,
            }
        }
    
    def generate_auto_fix(self, finding_data: dict, file_patch: str) -> str:
        """Generate an AI code fix for a specific finding.
        
        Returns a unified diff patch string that can be applied.
        """
        try:
            prompt = f"""You are a senior software engineer. Generate a PRECISE code fix for this issue.

**Issue:**
- Title: {finding_data.get('title', '')}
- Severity: {finding_data.get('severity', '')}
- File: {finding_data.get('file_path', '')}
- Line: {finding_data.get('line_number', 'unknown')}
- Description: {finding_data.get('description', '')}
- Suggestion: {finding_data.get('suggestion', '')}

**Current Code (diff context):**
```
{file_patch[:3000]}
```

Generate the fix as a unified diff patch. Return ONLY the diff, no explanation.
Format:
```diff
--- a/{finding_data.get('file_path', 'file')}
+++ b/{finding_data.get('file_path', 'file')}
@@ ... @@
 context line
-old line
+new line
 context line
```"""
            
            result = self._call_llm_raw(
                "You are an expert programmer. Generate precise, minimal code fixes as unified diff patches. Return ONLY the diff, no markdown wrapping, no explanation.",
                prompt
            )
            
            # Clean up response
            result = result.strip()
            if result.startswith("```"):
                lines = result.split("\n")
                result = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            
            return result.strip()
        except Exception as e:
            logger.error(f"Auto-fix generation failed: {e}")
            return ""
    
    def generate_pr_summary(self, diff_data: list, findings: list, run_metadata: dict) -> str:
        """Generate a natural language PR summary for non-technical stakeholders.
        
        Returns a human-readable summary paragraph.
        """
        try:
            file_list = "\n".join(f"- {f.get('filename', '?')} (+{f.get('additions', 0)} -{f.get('deletions', 0)})" for f in diff_data[:20])
            finding_list = "\n".join(f"- [{f.get('severity', '?')}] {f.get('title', '?')} in {f.get('file_path', '?')}" for f in findings[:15])
            
            prompt = f"""Summarize this Pull Request for a non-technical project manager or stakeholder.

**Changed Files ({len(diff_data)}):**
{file_list}

**Code Review Findings ({len(findings)}):**
{finding_list or 'No issues found.'}

**Metrics:**
- Files analyzed: {run_metadata.get('files_analyzed', len(diff_data))}
- Total findings: {run_metadata.get('findings_count', len(findings))}
- AI-detected issues: {run_metadata.get('ai_findings', 0)}

Write a 3-5 sentence summary that covers:
1. What this PR changes (infer from file names)
2. Overall quality assessment
3. Key risks or concerns (if any)
4. Recommendation (safe to merge / needs attention / block merge)

Use plain English, no jargon. Be concise."""
            
            return self._call_llm_raw(
                "You are a technical writer who translates code reviews into plain English for non-technical stakeholders. Be clear, concise, and actionable.",
                prompt
            )
        except Exception as e:
            logger.error(f"PR summary generation failed: {e}")
            return ""
    
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
                    "finding_metadata": {"source": "llm", "provider": self.provider}
                }
                findings.append(finding)
            
            logger.info(f"Parsed {len(findings)} findings from LLM response")
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}\nResponse: {response[:200]}")
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}")
        
        return findings
