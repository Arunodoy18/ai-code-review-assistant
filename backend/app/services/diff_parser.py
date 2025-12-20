"""
Diff parser for extracting changed hunks and lines from GitHub PR diffs
"""
import re
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class DiffParser:
    """Parse unified diff format from GitHub PRs"""
    
    @staticmethod
    def parse_patch(patch: str, filename: str) -> Dict:
        """
        Parse a unified diff patch and extract changed lines
        
        Returns dict with:
        - hunks: List of changed hunks with line ranges
        - added_lines: Dict mapping line numbers to added code
        - removed_lines: Dict mapping line numbers to removed code
        - context: Full context for each hunk
        """
        if not patch:
            return {
                "hunks": [],
                "added_lines": {},
                "removed_lines": {},
                "context": []
            }
        
        hunks = []
        added_lines = {}
        removed_lines = {}
        
        lines = patch.split('\n')
        current_hunk = None
        old_line_no = 0
        new_line_no = 0
        
        for line in lines:
            # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
            hunk_match = re.match(r'^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@', line)
            if hunk_match:
                if current_hunk:
                    hunks.append(current_hunk)
                
                old_start = int(hunk_match.group(1))
                old_count = int(hunk_match.group(2) or 1)
                new_start = int(hunk_match.group(3))
                new_count = int(hunk_match.group(4) or 1)
                
                old_line_no = old_start
                new_line_no = new_start
                
                current_hunk = {
                    "old_start": old_start,
                    "old_count": old_count,
                    "new_start": new_start,
                    "new_count": new_count,
                    "added": [],
                    "removed": [],
                    "context": []
                }
                continue
            
            if not current_hunk:
                continue
            
            # Added line
            if line.startswith('+'):
                code = line[1:]
                added_lines[new_line_no] = code
                current_hunk["added"].append({
                    "line_number": new_line_no,
                    "code": code
                })
                current_hunk["context"].append(line)
                new_line_no += 1
            
            # Removed line
            elif line.startswith('-'):
                code = line[1:]
                removed_lines[old_line_no] = code
                current_hunk["removed"].append({
                    "line_number": old_line_no,
                    "code": code
                })
                current_hunk["context"].append(line)
                old_line_no += 1
            
            # Context line (unchanged)
            elif line.startswith(' '):
                current_hunk["context"].append(line)
                old_line_no += 1
                new_line_no += 1
        
        # Add last hunk
        if current_hunk:
            hunks.append(current_hunk)
        
        return {
            "hunks": hunks,
            "added_lines": added_lines,
            "removed_lines": removed_lines,
            "filename": filename
        }
    
    @staticmethod
    def get_changed_line_numbers(patch: str) -> List[int]:
        """Extract just the added line numbers from a patch"""
        result = DiffParser.parse_patch(patch, "")
        return sorted(result["added_lines"].keys())
    
    @staticmethod
    def get_hunk_for_line(parsed_diff: Dict, line_number: int) -> Dict:
        """Get the hunk containing a specific line number"""
        for hunk in parsed_diff.get("hunks", []):
            start = hunk["new_start"]
            end = start + hunk["new_count"]
            if start <= line_number < end:
                return hunk
        return None
    
    @staticmethod
    def format_hunk_context(hunk: Dict, highlight_line: int = None) -> str:
        """
        Format a hunk for display with optional highlighting
        
        Args:
            hunk: Hunk dict from parse_patch
            highlight_line: Line number to highlight (optional)
        
        Returns:
            Formatted string with context
        """
        if not hunk:
            return ""
        
        lines = []
        lines.append(f"@@ -{hunk['old_start']},{hunk['old_count']} +{hunk['new_start']},{hunk['new_count']} @@")
        
        for context_line in hunk.get("context", []):
            if highlight_line:
                # Try to detect if this is the highlighted line
                if context_line.startswith('+'):
                    # Rough estimate - need to track line numbers properly
                    lines.append(f">>> {context_line}")
                else:
                    lines.append(context_line)
            else:
                lines.append(context_line)
        
        return '\n'.join(lines)
    
    @staticmethod
    def extract_function_context(patch: str, line_number: int) -> Tuple[str, int, int]:
        """
        Try to extract the function/method context for a given line
        
        Returns:
            (function_name, start_line, end_line)
        """
        parsed = DiffParser.parse_patch(patch, "")
        hunk = DiffParser.get_hunk_for_line(parsed, line_number)
        
        if not hunk:
            return None, 0, 0
        
        # Look for function definitions in context
        function_patterns = [
            r'^\s*(?:async\s+)?def\s+(\w+)\s*\(',  # Python
            r'^\s*(?:async\s+)?function\s+(\w+)\s*\(',  # JavaScript
            r'^\s*(?:public|private|protected)?\s*\w+\s+(\w+)\s*\(',  # Java/C++
        ]
        
        context = '\n'.join(hunk.get("context", []))
        for pattern in function_patterns:
            match = re.search(pattern, context, re.MULTILINE)
            if match:
                return match.group(1), hunk["new_start"], hunk["new_start"] + hunk["new_count"]
        
        return None, hunk["new_start"], hunk["new_start"] + hunk["new_count"]
