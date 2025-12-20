# 🛠️ Custom Rules Development Guide

Learn how to create custom analysis rules for the AI Code Review Assistant.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Rule Structure](#rule-structure)
- [Creating a New Rule](#creating-a-new-rule)
- [Rule Categories](#rule-categories)
- [Testing Your Rule](#testing-your-rule)
- [Best Practices](#best-practices)
- [Examples](#examples)

---

## Overview

The analysis engine supports two types of rules:

1. **Static Pattern Rules** - Regular expression-based matching
2. **AI-Powered Rules** - LLM-based deep analysis

This guide focuses on creating static pattern rules, which are faster and more predictable.

---

## Rule Structure

Every rule consists of:

```python
{
    "rule_id": "category.rule_name",
    "name": "Human-Readable Name",
    "description": "What this rule detects",
    "category": RuleCategory,  # security, bug, performance, style, etc.
    "default_severity": RuleSeverity,  # critical, high, medium, low
    "pattern": r"regex_pattern",  # Optional for pattern rules
    "languages": ["python", "javascript"],  # Applicable languages
    "suggestion": "How to fix the issue"
}
```

---

## Creating a New Rule

### Step 1: Define the Rule

Add your rule to `backend/app/services/config_service.py` in the `AVAILABLE_RULES` list:

```python
RuleDefinition(
    rule_id="security.insecure_random",
    name="Insecure Random Number Generation",
    description="Detects use of random.random() instead of secrets module for security-sensitive operations",
    category=RuleCategory.SECURITY,
    default_severity=RuleSeverity.HIGH,
    languages=["python"],
    configurable=True,
    requires_ai=False
)
```

### Step 2: Implement the Detection Logic

Add the detection logic in `backend/app/services/analyzer_service.py`:

```python
# In the analyze_line method
if language == "python":
    # Check for insecure random
    if re.search(r'random\.(random|randint|choice)', line):
        if 'import secrets' not in file_context:
            findings.append(Finding(
                file_path=file_path,
                line_number=line_number,
                severity=FindingSeverity.HIGH,
                category=FindingCategory.SECURITY,
                rule_id="security.insecure_random",
                title="Insecure Random Number Generation",
                description="Using random module for security-sensitive operations. Use secrets module instead.",
                suggestion="Replace: random.random() → secrets.SystemRandom().random()",
                code_snippet=line.strip(),
                is_ai_generated=0
            ))
```

### Step 3: Register the Rule

The rule is automatically available once added to `AVAILABLE_RULES`. Users can enable/disable it via the configuration API.

---

## Rule Categories

### Security Rules
**Prefix**: `security.*`
**Purpose**: Detect security vulnerabilities
**Examples**:
- `security.sql_injection`
- `security.xss`
- `security.hardcoded_secrets`

### Bug Detection Rules
**Prefix**: `bug.*` or `quality.*`
**Purpose**: Find potential bugs and logic errors
**Examples**:
- `bug.null_pointer`
- `quality.missing_error_handling`
- `bug.race_condition`

### Performance Rules
**Prefix**: `performance.*`
**Purpose**: Identify performance bottlenecks
**Examples**:
- `performance.n_plus_one_query`
- `performance.inefficient_loop`
- `performance.memory_leak`

### Style Rules
**Prefix**: `style.*` or `quality.*`
**Purpose**: Enforce coding standards
**Examples**:
- `style.console_log`
- `quality.magic_numbers`
- `style.line_too_long`

### Best Practice Rules
**Prefix**: `best_practice.*`
**Purpose**: Promote good coding practices
**Examples**:
- `best_practice.missing_docstring`
- `best_practice.missing_type_hints`
- `best_practice.missing_tests`

---

## Testing Your Rule

### Unit Test Template

Create a test in `backend/tests/test_custom_rules.py`:

```python
def test_insecure_random_detection():
    """Test detection of insecure random usage"""
    # Arrange
    analyzer = AnalyzerService()
    test_code = "token = random.randint(1000, 9999)"
    
    # Act
    findings = analyzer.analyze_line(
        test_code,
        "app/security.py",
        10,
        "python"
    )
    
    # Assert
    assert len(findings) > 0
    assert any(f.rule_id == "security.insecure_random" for f in findings)
    assert findings[0].severity == "high"
```

### Integration Test

Add to `backend/tests/test_integration.py`:

```python
def test_insecure_random_in_pr(db_session, test_project):
    """Test insecure random detection in PR context"""
    diff = '''
+import random
+def generate_token():
+    return random.randint(1000, 9999)
    '''
    
    analyzer = AnalyzerService()
    findings = []
    
    for line_num, line in enumerate(diff.split("\n"), start=1):
        if line.startswith("+"):
            findings.extend(analyzer.analyze_line(line[1:], "app/auth.py", line_num, "python"))
    
    assert any(f.rule_id == "security.insecure_random" for f in findings)
```

### Run Tests

```bash
cd backend
pytest tests/test_custom_rules.py::test_insecure_random_detection -v
```

---

## Best Practices

### 1. Clear Naming
✅ **Good**: `security.sql_injection`
❌ **Bad**: `sec_rule_1`

### 2. Precise Patterns
```python
# Good: Specific pattern
r'eval\s*\('

# Bad: Too broad
r'eval'
```

### 3. Helpful Suggestions
```python
suggestion="Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
```

### 4. Language-Specific Logic
```python
if language == "python":
    # Python-specific checks
elif language in ["javascript", "typescript"]:
    # JS/TS-specific checks
```

### 5. Avoid False Positives
```python
# Check context before flagging
if 'test' not in file_path.lower():  # Skip test files
    if pattern_match and not in_comment:
        # Flag the issue
```

---

## Examples

### Example 1: Detect Hardcoded IP Addresses

```python
RuleDefinition(
    rule_id="security.hardcoded_ip",
    name="Hardcoded IP Address",
    description="Detects hardcoded IP addresses that should be in configuration",
    category=RuleCategory.SECURITY,
    default_severity=RuleSeverity.MEDIUM,
    languages=["python", "javascript", "typescript", "java"],
    configurable=True,
    requires_ai=False
)

# Detection logic
if re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', line):
    if not re.search(r'(127\.0\.0\.1|0\.0\.0\.0|localhost)', line):
        findings.append(Finding(
            rule_id="security.hardcoded_ip",
            title="Hardcoded IP Address",
            description="IP address should be in configuration, not hardcoded",
            suggestion="Move IP address to environment variable or config file",
            severity=FindingSeverity.MEDIUM,
            category=FindingCategory.SECURITY,
            ...
        ))
```

### Example 2: Detect Missing Input Validation

```python
RuleDefinition(
    rule_id="security.missing_validation",
    name="Missing Input Validation",
    description="Detects user input used without validation",
    category=RuleCategory.SECURITY,
    default_severity=RuleSeverity.HIGH,
    languages=["python", "javascript"],
    configurable=True,
    requires_ai=False
)

# Detection logic (simplified)
if 'request.' in line or 'req.body' in line:
    # Check if there's validation nearby
    if not any(validator in context for validator in ['validate', 'sanitize', 'check']):
        findings.append(Finding(
            rule_id="security.missing_validation",
            title="Missing Input Validation",
            description="User input should be validated before use",
            suggestion="Add input validation using a validation library",
            severity=FindingSeverity.HIGH,
            category=FindingCategory.SECURITY,
            ...
        ))
```

### Example 3: Detect Deprecated API Usage

```python
RuleDefinition(
    rule_id="best_practice.deprecated_api",
    name="Deprecated API Usage",
    description="Detects use of deprecated APIs that should be updated",
    category=RuleCategory.BEST_PRACTICE,
    default_severity=RuleSeverity.MEDIUM,
    languages=["javascript", "typescript"],
    configurable=True,
    requires_ai=False
)

# Detection logic
deprecated_apis = {
    'componentWillMount': 'Use componentDidMount or constructor instead',
    'componentWillReceiveProps': 'Use getDerivedStateFromProps instead',
    'componentWillUpdate': 'Use componentDidUpdate instead'
}

for old_api, new_api in deprecated_apis.items():
    if old_api in line:
        findings.append(Finding(
            rule_id="best_practice.deprecated_api",
            title=f"Deprecated API: {old_api}",
            description=f"{old_api} is deprecated in React 17+",
            suggestion=new_api,
            severity=FindingSeverity.MEDIUM,
            category=FindingCategory.BEST_PRACTICE,
            ...
        ))
```

---

## Advanced: AI-Powered Rules

For complex patterns that need context understanding, mark the rule with `requires_ai=True`:

```python
RuleDefinition(
    rule_id="ai.business_logic_error",
    name="Business Logic Error",
    description="AI-detected business logic issues",
    category=RuleCategory.BUG,
    default_severity=RuleSeverity.HIGH,
    languages=["python", "javascript", "typescript", "java"],
    configurable=True,
    requires_ai=True  # This rule uses LLM analysis
)
```

AI rules are processed by the LLM service and don't need explicit pattern matching.

---

## Rule Lifecycle

1. **Development**: Create rule definition and detection logic
2. **Testing**: Write unit and integration tests
3. **Registration**: Add to `AVAILABLE_RULES` list
4. **Configuration**: Users can enable/disable via API
5. **Execution**: Rule runs during PR analysis
6. **Reporting**: Findings appear in dashboard and PR comments

---

## Troubleshooting

### Rule Not Firing
- Check language filter matches the file type
- Verify pattern regex is correct
- Ensure rule is enabled in project config

### Too Many False Positives
- Add context checks (e.g., skip test files)
- Make pattern more specific
- Add exclusion patterns

### Performance Issues
- Avoid complex regex patterns
- Use simple string matching when possible
- Consider caching results

---

## Next Steps

1. Review existing rules in `analyzer_service.py`
2. Create your custom rule
3. Write comprehensive tests
4. Submit a pull request with your rule
5. Update this documentation

---

## Resources

- [Regex Testing](https://regex101.com/)
- [Python re module](https://docs.python.org/3/library/re.html)
- [OWASP Security Guidelines](https://owasp.org/)
- [Static Analysis Best Practices](https://github.com/analysis-tools-dev/static-analysis)

---

**Happy Rule Development! 🎉**

*For questions or support, open an issue on GitHub.*
