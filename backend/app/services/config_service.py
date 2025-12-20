"""
Configuration service for managing project settings and rules
"""
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from app.models import Project
from app.schemas.config import ProjectConfigSchema, AnalysisConfig, RuleConfig, RuleSeverity, RuleCategory, RuleDefinition
import json


class ConfigurationService:
    """Service for managing project configurations"""
    
    # Define all available rules
    AVAILABLE_RULES: List[RuleDefinition] = [
        # Security Rules
        RuleDefinition(
            rule_id="security.eval_usage",
            name="Dangerous eval() Usage",
            description="Detects use of eval() which can execute arbitrary code",
            category=RuleCategory.SECURITY,
            default_severity=RuleSeverity.CRITICAL,
            languages=["python", "javascript", "typescript"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="security.sql_injection",
            name="SQL Injection Risk",
            description="Detects potential SQL injection vulnerabilities",
            category=RuleCategory.SECURITY,
            default_severity=RuleSeverity.CRITICAL,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="security.hardcoded_secrets",
            name="Hardcoded Secrets",
            description="Detects hardcoded passwords, API keys, and tokens",
            category=RuleCategory.SECURITY,
            default_severity=RuleSeverity.HIGH,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="security.command_injection",
            name="Command Injection",
            description="Detects unsafe command execution patterns",
            category=RuleCategory.SECURITY,
            default_severity=RuleSeverity.CRITICAL,
            languages=["python", "javascript", "typescript"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="security.unsafe_deserialization",
            name="Unsafe Deserialization",
            description="Detects unsafe deserialization (pickle, yaml.load)",
            category=RuleCategory.SECURITY,
            default_severity=RuleSeverity.HIGH,
            languages=["python"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="security.weak_cryptography",
            name="Weak Cryptography",
            description="Detects use of weak cryptographic algorithms",
            category=RuleCategory.SECURITY,
            default_severity=RuleSeverity.HIGH,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="security.path_traversal",
            name="Path Traversal",
            description="Detects potential path traversal vulnerabilities",
            category=RuleCategory.SECURITY,
            default_severity=RuleSeverity.HIGH,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=False
        ),
        
        # Code Quality Rules
        RuleDefinition(
            rule_id="quality.console_log",
            name="Console Log Statement",
            description="Detects console.log/print statements in production code",
            category=RuleCategory.STYLE,
            default_severity=RuleSeverity.LOW,
            languages=["javascript", "typescript", "python"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="quality.missing_error_handling",
            name="Missing Error Handling",
            description="Detects operations without proper try-catch",
            category=RuleCategory.BUG,
            default_severity=RuleSeverity.MEDIUM,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="quality.unused_variables",
            name="Unused Variables",
            description="Detects declared but unused variables",
            category=RuleCategory.STYLE,
            default_severity=RuleSeverity.LOW,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="quality.duplicate_code",
            name="Duplicate Code",
            description="Detects code duplication that should be refactored",
            category=RuleCategory.BEST_PRACTICE,
            default_severity=RuleSeverity.MEDIUM,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="quality.magic_numbers",
            name="Magic Numbers",
            description="Detects numeric literals that should be named constants",
            category=RuleCategory.BEST_PRACTICE,
            default_severity=RuleSeverity.LOW,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="quality.long_function",
            name="Long Function",
            description="Detects functions that are too long and should be split",
            category=RuleCategory.BEST_PRACTICE,
            default_severity=RuleSeverity.MEDIUM,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="quality.deep_nesting",
            name="Deep Nesting",
            description="Detects deeply nested code blocks",
            category=RuleCategory.STYLE,
            default_severity=RuleSeverity.MEDIUM,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=False
        ),
        
        # Performance Rules
        RuleDefinition(
            rule_id="performance.n_plus_one_query",
            name="N+1 Query Problem",
            description="Detects inefficient database query patterns",
            category=RuleCategory.PERFORMANCE,
            default_severity=RuleSeverity.HIGH,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="performance.inefficient_loop",
            name="Inefficient Loop",
            description="Detects inefficient loop patterns and operations",
            category=RuleCategory.PERFORMANCE,
            default_severity=RuleSeverity.MEDIUM,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="performance.memory_leak",
            name="Memory Leak Risk",
            description="Detects patterns that may cause memory leaks",
            category=RuleCategory.PERFORMANCE,
            default_severity=RuleSeverity.HIGH,
            languages=["javascript", "typescript"],
            configurable=True,
            requires_ai=False
        ),
        
        # Best Practice Rules
        RuleDefinition(
            rule_id="best_practice.missing_type_hints",
            name="Missing Type Hints",
            description="Detects functions without type annotations",
            category=RuleCategory.BEST_PRACTICE,
            default_severity=RuleSeverity.LOW,
            languages=["python", "typescript"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="best_practice.missing_docstring",
            name="Missing Docstring",
            description="Detects functions without documentation",
            category=RuleCategory.DOCUMENTATION,
            default_severity=RuleSeverity.LOW,
            languages=["python"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="best_practice.missing_tests",
            name="Missing Tests",
            description="Detects code without corresponding tests",
            category=RuleCategory.BEST_PRACTICE,
            default_severity=RuleSeverity.MEDIUM,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=False
        ),
        RuleDefinition(
            rule_id="best_practice.broad_exception",
            name="Broad Exception Handling",
            description="Detects overly broad exception catching",
            category=RuleCategory.BEST_PRACTICE,
            default_severity=RuleSeverity.MEDIUM,
            languages=["python", "java"],
            configurable=True,
            requires_ai=False
        ),
        
        # AI-Powered Rules
        RuleDefinition(
            rule_id="ai.logic_error",
            name="AI-Detected Logic Error",
            description="AI-detected logical errors and edge cases",
            category=RuleCategory.BUG,
            default_severity=RuleSeverity.HIGH,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=True
        ),
        RuleDefinition(
            rule_id="ai.race_condition",
            name="AI-Detected Race Condition",
            description="AI-detected concurrency and threading issues",
            category=RuleCategory.BUG,
            default_severity=RuleSeverity.CRITICAL,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=True
        ),
        RuleDefinition(
            rule_id="ai.security_vulnerability",
            name="AI-Detected Security Issue",
            description="AI-detected security vulnerabilities beyond static rules",
            category=RuleCategory.SECURITY,
            default_severity=RuleSeverity.HIGH,
            languages=["python", "javascript", "typescript", "java"],
            configurable=True,
            requires_ai=True
        ),
    ]
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_project_config(self, project_id: int) -> ProjectConfigSchema:
        """Get configuration for a project"""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Parse config from JSON or return defaults
        config_dict = project.config or {}
        
        # Build ProjectConfigSchema
        return ProjectConfigSchema(
            project_id=project_id,
            enabled_rules=config_dict.get("enabled_rules", []),
            disabled_rules=config_dict.get("disabled_rules", []),
            rule_configs=self._parse_rule_configs(config_dict.get("rule_configs", {})),
            analysis_config=self._parse_analysis_config(config_dict.get("analysis_config", {})),
            exclude_paths=config_dict.get("exclude_paths", ["**/node_modules/**", "**/dist/**", "**/build/**"]),
            include_paths=config_dict.get("include_paths", ["**/*.py", "**/*.js", "**/*.ts", "**/*.tsx", "**/*.java"])
        )
    
    def update_project_config(self, project_id: int, updates: Dict) -> ProjectConfigSchema:
        """Update project configuration"""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Get current config
        current_config = project.config or {}
        
        # Merge updates
        for key, value in updates.items():
            if value is not None:
                if key == "rule_configs":
                    current_config[key] = {k: v.dict() if hasattr(v, 'dict') else v 
                                          for k, v in value.items()}
                elif key == "analysis_config":
                    current_config[key] = value.dict() if hasattr(value, 'dict') else value
                else:
                    current_config[key] = value
        
        # Save to database
        project.config = current_config
        self.db.commit()
        
        return self.get_project_config(project_id)
    
    def is_rule_enabled(self, project_id: int, rule_id: str) -> bool:
        """Check if a rule is enabled for a project"""
        config = self.get_project_config(project_id)
        
        # If in disabled list, return False
        if rule_id in config.disabled_rules:
            return False
        
        # If enabled_rules is empty, all rules enabled by default
        if not config.enabled_rules:
            return True
        
        # Otherwise check if in enabled list
        return rule_id in config.enabled_rules
    
    def get_rule_severity(self, project_id: int, rule_id: str) -> Optional[RuleSeverity]:
        """Get effective severity for a rule (considering overrides)"""
        config = self.get_project_config(project_id)
        
        # Check for rule-specific override
        if rule_id in config.rule_configs:
            return config.rule_configs[rule_id].severity
        
        # Return default severity from rule definition
        rule_def = self.get_rule_definition(rule_id)
        return rule_def.default_severity if rule_def else None
    
    def get_rule_definition(self, rule_id: str) -> Optional[RuleDefinition]:
        """Get rule definition by ID"""
        for rule in self.AVAILABLE_RULES:
            if rule.rule_id == rule_id:
                return rule
        return None
    
    def get_all_rules(self, category: Optional[str] = None, 
                     language: Optional[str] = None) -> List[RuleDefinition]:
        """Get all available rules, optionally filtered"""
        rules = self.AVAILABLE_RULES
        
        if category:
            rules = [r for r in rules if r.category == category]
        
        if language:
            rules = [r for r in rules if language in r.languages or not r.languages]
        
        return rules
    
    def get_enabled_rules(self, project_id: int) -> List[str]:
        """Get list of enabled rule IDs for a project"""
        config = self.get_project_config(project_id)
        
        # Get all rule IDs
        all_rule_ids = [r.rule_id for r in self.AVAILABLE_RULES]
        
        # Filter by enabled/disabled lists
        if config.enabled_rules:
            enabled = set(config.enabled_rules) - set(config.disabled_rules)
        else:
            enabled = set(all_rule_ids) - set(config.disabled_rules)
        
        return list(enabled)
    
    def _parse_rule_configs(self, configs: Dict) -> Dict[str, RuleConfig]:
        """Parse rule configs from dict"""
        result = {}
        for rule_id, config in configs.items():
            if isinstance(config, dict):
                result[rule_id] = RuleConfig(**config)
            else:
                result[rule_id] = config
        return result
    
    def _parse_analysis_config(self, config: Dict) -> AnalysisConfig:
        """Parse analysis config from dict"""
        if not config:
            return AnalysisConfig()
        return AnalysisConfig(**config)
