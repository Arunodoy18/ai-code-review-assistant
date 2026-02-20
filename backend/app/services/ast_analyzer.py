"""AST Analyzer Service using tree-sitter for code structure analysis"""
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# tree-sitter is loaded lazily inside ASTAnalyzer.__init__ to avoid
# heavy native-library loading at import time (cloud-safe startup).


class ASTAnalyzer:
    """Analyzes code structure using tree-sitter AST parsing"""
    
    def __init__(self):
        """Initialize AST analyzer with language parsers"""
        try:
            from tree_sitter import Language, Parser
            import tree_sitter_python
            import tree_sitter_javascript
            import tree_sitter_typescript

            self._Language = Language
            self._Parser = Parser
            # Initialize parsers for different languages
            self.parsers = {
                "python": self._create_parser(Language(tree_sitter_python.language())),
                "javascript": self._create_parser(Language(tree_sitter_javascript.language())),
                "typescript": self._create_parser(Language(tree_sitter_typescript.language_typescript())),
            }
            self._available = True
        except Exception as exc:
            logger.warning("tree-sitter not available (%s). AST analysis will be disabled.", exc)
            self.parsers = {}
            self._available = False
    
    def _create_parser(self, language) -> 'object':
        """Create a parser for a specific language"""
        parser = self._Parser()
        parser.set_language(language)
        return parser
    
    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code and extract structural information.
        
        Args:
            code: Source code string
            language: Programming language (python, javascript, typescript, etc.)
        
        Returns:
            Dictionary containing:
            - functions: List of function definitions
            - classes: List of class definitions
            - imports: List of import statements
            - exports: List of export statements (JS/TS)
            - complexity: Code complexity metrics
            - structure: High-level code structure
        """
        if not self._available:
            return self._empty_analysis()
        
        parser = self.parsers.get(language)
        if not parser:
            logger.debug(f"No parser available for language: {language}")
            return self._empty_analysis()
        
        try:
            tree = parser.parse(bytes(code, "utf8"))
            root_node = tree.root_node
            
            if language == "python":
                return self._analyze_python(root_node, code)
            elif language in ["javascript", "typescript"]:
                return self._analyze_javascript(root_node, code)
            else:
                return self._empty_analysis()
                
        except Exception as e:
            logger.error(f"AST parsing failed for {language}: {e}")
            return self._empty_analysis()
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis result"""
        return {
            "functions": [],
            "classes": [],
            "imports": [],
            "exports": [],
            "complexity": 0,
            "structure": ""
        }
    
    def _analyze_python(self, root_node, code: str) -> Dict[str, Any]:
        """Analyze Python code structure"""
        functions = []
        classes = []
        imports = []
        
        # Extract functions
        for node in self._find_nodes_by_type(root_node, "function_definition"):
            func_name = self._get_node_text(node.child_by_field_name("name"), code)
            params = self._extract_python_params(node, code)
            line_number = node.start_point[0] + 1
            
            functions.append({
                "name": func_name,
                "params": params,
                "line": line_number,
                "type": "function"
            })
        
        # Extract classes
        for node in self._find_nodes_by_type(root_node, "class_definition"):
            class_name = self._get_node_text(node.child_by_field_name("name"), code)
            line_number = node.start_point[0] + 1
            
            # Extract methods within class
            methods = []
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    if child.type == "function_definition":
                        method_name = self._get_node_text(child.child_by_field_name("name"), code)
                        methods.append(method_name)
            
            classes.append({
                "name": class_name,
                "line": line_number,
                "methods": methods,
                "type": "class"
            })
        
        # Extract imports
        for node in self._find_nodes_by_type(root_node, "import_statement") + \
                     self._find_nodes_by_type(root_node, "import_from_statement"):
            import_text = self._get_node_text(node, code)
            imports.append(import_text.strip())
        
        # Calculate complexity (count of decision points)
        complexity = self._calculate_complexity(root_node)
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "exports": [],
            "complexity": complexity,
            "structure": self._summarize_structure(functions, classes)
        }
    
    def _analyze_javascript(self, root_node, code: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code structure"""
        functions = []
        classes = []
        imports = []
        exports = []
        
        # Extract function declarations
        for node in self._find_nodes_by_type(root_node, "function_declaration"):
            func_name = self._get_node_text(node.child_by_field_name("name"), code)
            line_number = node.start_point[0] + 1
            functions.append({
                "name": func_name,
                "line": line_number,
                "type": "function"
            })
        
        # Extract arrow functions and method definitions
        for node in self._find_nodes_by_type(root_node, "arrow_function") + \
                     self._find_nodes_by_type(root_node, "method_definition"):
            line_number = node.start_point[0] + 1
            # Try to get identifier from parent
            name = "anonymous"
            if node.parent and node.parent.type == "variable_declarator":
                name_node = node.parent.child_by_field_name("name")
                if name_node:
                    name = self._get_node_text(name_node, code)
            
            functions.append({
                "name": name,
                "line": line_number,
                "type": "function"
            })
        
        # Extract classes
        for node in self._find_nodes_by_type(root_node, "class_declaration"):
            class_name = self._get_node_text(node.child_by_field_name("name"), code)
            line_number = node.start_point[0] + 1
            classes.append({
                "name": class_name,
                "line": line_number,
                "type": "class"
            })
        
        # Extract imports
        for node in self._find_nodes_by_type(root_node, "import_statement"):
            import_text = self._get_node_text(node, code)
            imports.append(import_text.strip())
        
        # Extract exports
        for node in self._find_nodes_by_type(root_node, "export_statement"):
            export_text = self._get_node_text(node, code)
            exports.append(export_text.strip())
        
        complexity = self._calculate_complexity(root_node)
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "exports": exports,
            "complexity": complexity,
            "structure": self._summarize_structure(functions, classes)
        }
    
    def _find_nodes_by_type(self, node, node_type: str) -> List:
        """Recursively find all nodes of a specific type"""
        results = []
        
        if node.type == node_type:
            results.append(node)
        
        for child in node.children:
            results.extend(self._find_nodes_by_type(child, node_type))
        
        return results
    
    def _get_node_text(self, node, code: str) -> str:
        """Extract text content of a node"""
        if node is None:
            return ""
        return code[node.start_byte:node.end_byte]
    
    def _extract_python_params(self, func_node, code: str) -> List[str]:
        """Extract parameter names from Python function"""
        params = []
        params_node = func_node.child_by_field_name("parameters")
        if params_node:
            for child in params_node.children:
                if child.type == "identifier":
                    params.append(self._get_node_text(child, code))
        return params
    
    def _calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity (count of decision points)"""
        complexity = 1  # Base complexity
        
        decision_nodes = [
            "if_statement",
            "while_statement",
            "for_statement",
            "conditional_expression",
            "boolean_operator",
            "case_statement",
        ]
        
        for decision_type in decision_nodes:
            complexity += len(self._find_nodes_by_type(node, decision_type))
        
        return complexity
    
    def _summarize_structure(self, functions: List[Dict], classes: List[Dict]) -> str:
        """Generate a text summary of code structure"""
        parts = []
        
        if classes:
            class_names = [c["name"] for c in classes]
            parts.append(f"Classes: {', '.join(class_names)}")
        
        if functions:
            func_count = len(functions)
            parts.append(f"{func_count} functions")
        
        return " | ".join(parts) if parts else "No major structures"
    
    def analyze_changes_impact(
        self,
        old_analysis: Dict[str, Any],
        new_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare two AST analyses to understand impact of changes.
        
        Returns:
            Dictionary with:
            - added_functions: New functions
            - removed_functions: Deleted functions
            - modified_functions: Changed function signatures
            - added_classes: New classes
            - removed_classes: Deleted classes
            - import_changes: Changed imports
        """
        old_func_names = {f["name"] for f in old_analysis.get("functions", [])}
        new_func_names = {f["name"] for f in new_analysis.get("functions", [])}
        
        old_class_names = {c["name"] for c in old_analysis.get("classes", [])}
        new_class_names = {c["name"] for c in new_analysis.get("classes", [])}
        
        return {
            "added_functions": list(new_func_names - old_func_names),
            "removed_functions": list(old_func_names - new_func_names),
            "modified_functions": list(old_func_names & new_func_names),
            "added_classes": list(new_class_names - old_class_names),
            "removed_classes": list(old_class_names - new_class_names),
            "import_changes": {
                "old": old_analysis.get("imports", []),
                "new": new_analysis.get("imports", [])
            },
            "complexity_delta": new_analysis.get("complexity", 0) - old_analysis.get("complexity", 0)
        }


# Singleton instance
_ast_analyzer = None

def get_ast_analyzer() -> ASTAnalyzer:
    """Get or create the AST analyzer singleton"""
    global _ast_analyzer
    if _ast_analyzer is None:
        _ast_analyzer = ASTAnalyzer()
    return _ast_analyzer
