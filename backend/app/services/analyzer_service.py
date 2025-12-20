from app.models import FindingSeverity, FindingCategory
import re
import logging

logger = logging.getLogger(__name__)


class AnalyzerService:
    """Service for rule-based static analysis"""
    
    def __init__(self, project_config: dict = None):
        self.config = project_config or {}
        self.enabled_rules = self.config.get("enabled_rules", self._default_rules())
    
    def _default_rules(self) -> list:
        """Default rules to check"""
        return [
            # Security
            "no_eval",
            "sql_injection_risk",
            "hardcoded_secrets",
            "command_injection",
            "unsafe_deserialization",
            "weak_crypto",
            "path_traversal",
            
            # Code Quality
            "no_console_log",
            "missing_error_handling",
            "unused_variables",
            "duplicate_code",
            "magic_numbers",
            "long_functions",
            "deep_nesting",
            
            # Performance
            "n_plus_one_query",
            "inefficient_loop",
            "memory_leak_risk",
            
            # Best Practices
            "missing_type_hints",
            "missing_docstrings",
            "missing_tests",
            "improper_exception_handling"
        ]
    
    def analyze_diff(self, diff_data: list) -> list:
        """Analyze diff and return findings"""
        findings = []
        
        for file_data in diff_data:
            filename = file_data["filename"]
            patch = file_data.get("patch")
            
            if not patch:
                continue
            
            # Skip non-code files
            if not self._is_code_file(filename):
                continue
            
            # Run checks on patch
            file_findings = self._check_file(filename, patch)
            findings.extend(file_findings)
        
        return findings
    
    def _is_code_file(self, filename: str) -> bool:
        """Check if file is a code file"""
        code_extensions = [
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c',
            '.go', '.rb', '.php', '.swift', '.kt', '.rs', '.scala'
        ]
        return any(filename.endswith(ext) for ext in code_extensions)
    
    def _check_file(self, filename: str, patch: str) -> list:
        """Run all enabled checks on file"""
        findings = []
        
        lines = patch.split('\n')
        line_number = 0
        
        for line in lines:
            # Track line numbers from patch
            if line.startswith('@@'):
                match = re.search(r'\+(\d+)', line)
                if match:
                    line_number = int(match.group(1))
                continue
            
            if line.startswith('+'):
                line_number += 1
                code = line[1:]  # Remove '+' prefix
                
                # Run checks
                if "no_console_log" in self.enabled_rules:
                    finding = self._check_console_log(filename, line_number, code)
                    if finding:
                        findings.append(finding)
                
                if "no_eval" in self.enabled_rules:
                    finding = self._check_eval(filename, line_number, code)
                    if finding:
                        findings.append(finding)
                
                if "sql_injection_risk" in self.enabled_rules:
                    finding = self._check_sql_injection(filename, line_number, code)
                    if finding:
                        findings.append(finding)
                
                if "hardcoded_secrets" in self.enabled_rules:
                    finding = self._check_hardcoded_secrets(filename, line_number, code)
                    if finding:
                        findings.append(finding)
                
                if "command_injection" in self.enabled_rules:
                    finding = self._check_command_injection(filename, line_number, code)
                    if finding:
                        findings.append(finding)
                
                if "unsafe_deserialization" in self.enabled_rules:
                    finding = self._check_unsafe_deserialization(filename, line_number, code)
                    if finding:
                        findings.append(finding)
                
                if "weak_crypto" in self.enabled_rules:
                    finding = self._check_weak_crypto(filename, line_number, code)
                    if finding:
                        findings.append(finding)
                
                if "path_traversal" in self.enabled_rules:
                    finding = self._check_path_traversal(filename, line_number, code)
                    if finding:
                        findings.append(finding)
                
                if "magic_numbers" in self.enabled_rules:
                    finding = self._check_magic_numbers(filename, line_number, code)
                    if finding:
                        findings.append(finding)
                
                if "missing_error_handling" in self.enabled_rules:
                    finding = self._check_missing_error_handling(filename, line_number, code)
                    if finding:
                        findings.append(finding)
        
        return findings
    
    def _check_console_log(self, filename: str, line_number: int, code: str) -> dict:
        """Check for console.log statements"""
        if re.search(r'console\.(log|debug|info)', code):
            return {
                "file_path": filename,
                "line_number": line_number,
                "severity": FindingSeverity.LOW,
                "category": FindingCategory.STYLE,
                "rule_id": "no_console_log",
                "title": "Console log statement found",
                "description": "Remove console.log statements before committing to production",
                "suggestion": "Use proper logging library or remove debug statements",
                "code_snippet": code.strip(),
                "is_ai_generated": 0
            }
        return None
    
    def _check_eval(self, filename: str, line_number: int, code: str) -> dict:
        """Check for eval() usage"""
        if re.search(r'\beval\s*\(', code):
            return {
                "file_path": filename,
                "line_number": line_number,
                "severity": FindingSeverity.CRITICAL,
                "category": FindingCategory.SECURITY,
                "rule_id": "no_eval",
                "title": "Dangerous eval() usage detected",
                "description": "eval() can execute arbitrary code and poses a security risk",
                "suggestion": "Avoid using eval(). Use safer alternatives like JSON.parse() or Function constructor",
                "code_snippet": code.strip(),
                "is_ai_generated": 0
            }
        return None
    
    def _check_sql_injection(self, filename: str, line_number: int, code: str) -> dict:
        """Check for potential SQL injection"""
        if re.search(r'(execute|query|raw)\s*\([^)]*[\+\%\{]', code):
            return {
                "file_path": filename,
                "line_number": line_number,
                "severity": FindingSeverity.HIGH,
                "category": FindingCategory.SECURITY,
                "rule_id": "sql_injection_risk",
                "title": "Potential SQL injection vulnerability",
                "description": "String concatenation in SQL queries can lead to SQL injection",
                "suggestion": "Use parameterized queries or prepared statements",
                "code_snippet": code.strip(),
                "is_ai_generated": 0
            }
        return None
    
    def _check_hardcoded_secrets(self, filename: str, line_number: int, code: str) -> dict:
        """Check for hardcoded secrets"""
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']{4,}["\']', 'password'),
            (r'api[_-]?key\s*=\s*["\'][^"\']{10,}["\']', 'API key'),
            (r'secret\s*=\s*["\'][^"\']{10,}["\']', 'secret'),
            (r'token\s*=\s*["\'][^"\']{10,}["\']', 'token'),
        ]
        
        for pattern, secret_type in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return {
                    "file_path": filename,
                    "line_number": line_number,
                    "severity": FindingSeverity.CRITICAL,
                    "category": FindingCategory.SECURITY,
                    "rule_id": "hardcoded_secrets",
                    "title": f"Hardcoded {secret_type} detected",
                    "description": f"Hardcoded {secret_type} found in code. This is a security risk.",
                    "suggestion": "Use environment variables or secret management systems",
                    "code_snippet": code.strip(),
                    "is_ai_generated": 0
                }
        return None
    
    def _check_command_injection(self, filename: str, line_number: int, code: str) -> dict:
        """Check for command injection vulnerabilities"""
        patterns = [
            (r'os\.system\s*\([^)]*[\+\%\{]', 'os.system with string concatenation'),
            (r'subprocess\.(call|run|Popen)\s*\([^)]*[\+\%\{]', 'subprocess with string concatenation'),
            (r'exec\s*\(', 'exec() call'),
            (r'shell\s*=\s*True', 'shell=True in subprocess'),
        ]
        
        for pattern, desc in patterns:
            if re.search(pattern, code):
                return {
                    "file_path": filename,
                    "line_number": line_number,
                    "severity": FindingSeverity.CRITICAL,
                    "category": FindingCategory.SECURITY,
                    "rule_id": "command_injection",
                    "title": f"Command injection risk: {desc}",
                    "description": "Executing shell commands with user input can lead to command injection",
                    "suggestion": "Use parameterized commands, avoid shell=True, validate and sanitize inputs",
                    "code_snippet": code.strip(),
                    "is_ai_generated": 0
                }
        return None
    
    def _check_unsafe_deserialization(self, filename: str, line_number: int, code: str) -> dict:
        """Check for unsafe deserialization"""
        patterns = [
            (r'pickle\.loads?\s*\(', 'pickle'),
            (r'yaml\.load\s*\([^,)]*\)', 'yaml.load without SafeLoader'),
            (r'json\.loads?\s*\([^)]*user', 'JSON from user input'),
        ]
        
        for pattern, desc in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return {
                    "file_path": filename,
                    "line_number": line_number,
                    "severity": FindingSeverity.HIGH,
                    "category": FindingCategory.SECURITY,
                    "rule_id": "unsafe_deserialization",
                    "title": f"Unsafe deserialization: {desc}",
                    "description": "Deserializing untrusted data can lead to remote code execution",
                    "suggestion": "Use yaml.safe_load(), validate data structure, avoid pickle for untrusted data",
                    "code_snippet": code.strip(),
                    "is_ai_generated": 0
                }
        return None
    
    def _check_weak_crypto(self, filename: str, line_number: int, code: str) -> dict:
        """Check for weak cryptography"""
        patterns = [
            (r'\bMD5\b|\bmd5\b', 'MD5 hash'),
            (r'\bSHA1\b|\bsha1\b', 'SHA1 hash'),
            (r'\bDES\b', 'DES encryption'),
            (r'Random\(\)', 'Random() instead of secrets'),
        ]
        
        for pattern, desc in patterns:
            if re.search(pattern, code):
                return {
                    "file_path": filename,
                    "line_number": line_number,
                    "severity": FindingSeverity.MEDIUM,
                    "category": FindingCategory.SECURITY,
                    "rule_id": "weak_crypto",
                    "title": f"Weak cryptography: {desc}",
                    "description": "Using weak or outdated cryptographic algorithms",
                    "suggestion": "Use SHA256+, AES-256, secrets module for random values",
                    "code_snippet": code.strip(),
                    "is_ai_generated": 0
                }
        return None
    
    def _check_path_traversal(self, filename: str, line_number: int, code: str) -> dict:
        """Check for path traversal vulnerabilities"""
        if re.search(r'open\s*\([^)]*[\+\%\{]', code):
            return {
                "file_path": filename,
                "line_number": line_number,
                "severity": FindingSeverity.HIGH,
                "category": FindingCategory.SECURITY,
                "rule_id": "path_traversal",
                "title": "Path traversal risk in file operations",
                "description": "File paths constructed from user input can lead to path traversal attacks",
                "suggestion": "Validate file paths, use os.path.basename(), restrict to allowed directories",
                "code_snippet": code.strip(),
                "is_ai_generated": 0
            }
        return None
    
    def _check_magic_numbers(self, filename: str, line_number: int, code: str) -> dict:
        """Check for magic numbers"""
        # Look for numeric literals (except 0, 1, -1, 100) outside of assignments to constants
        if re.search(r'(?<![A-Z_])\b(?!0\b|1\b|-1\b|100\b)\d{2,}\b', code):
            if not re.search(r'^[A-Z_]+=', code.strip()):  # Not a constant definition
                return {
                    "file_path": filename,
                    "line_number": line_number,
                    "severity": FindingSeverity.LOW,
                    "category": FindingCategory.BEST_PRACTICE,
                    "rule_id": "magic_numbers",
                    "title": "Magic number detected",
                    "description": "Numeric literals should be defined as named constants",
                    "suggestion": "Extract to a named constant with descriptive name",
                    "code_snippet": code.strip(),
                    "is_ai_generated": 0
                }
        return None
    
    def _check_missing_error_handling(self, filename: str, line_number: int, code: str) -> dict:
        """Check for missing error handling in risky operations"""
        risky_patterns = [
            (r'requests\.get|requests\.post', 'HTTP request'),
            (r'open\s*\(', 'file operation'),
            (r'json\.loads?', 'JSON parsing'),
            (r'int\(|float\(', 'type conversion'),
        ]
        
        for pattern, operation in risky_patterns:
            if re.search(pattern, code):
                # Simple heuristic: check if not in try block (rough check)
                if 'try' not in code.lower():
                    return {
                        "file_path": filename,
                        "line_number": line_number,
                        "severity": FindingSeverity.MEDIUM,
                        "category": FindingCategory.BUG,
                        "rule_id": "missing_error_handling",
                        "title": f"Missing error handling for {operation}",
                        "description": f"{operation} without proper error handling can cause crashes",
                        "suggestion": "Wrap in try-except block with appropriate error handling",
                        "code_snippet": code.strip(),
                        "is_ai_generated": 0
                    }
        return None
