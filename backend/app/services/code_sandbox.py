"""Code Sandbox Service using Docker for safe code execution"""
import logging
import tempfile
import os
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    logger.debug("docker package not available. Code sandbox will be disabled.")
    DOCKER_AVAILABLE = False


class CodeSandbox:
    """Safely execute code in isolated Docker containers"""
    
    def __init__(self):
        """Initialize Docker client"""
        self.client = None
        
        if not DOCKER_AVAILABLE:
            logger.debug("Code sandbox disabled - docker package not installed")
            return
        
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if sandbox is available"""
        return self.client is not None
    
    def test_python_code(
        self,
        code: str,
        test_code: Optional[str] = None,
        timeout: int = 10,
        memory_limit: str = "128m"
    ) -> Dict[str, Any]:
        """Execute Python code in a sandboxed environment.
        
        Args:
            code: Python code to execute
            test_code: Optional test code to run after main code
            timeout: Maximum execution time in seconds
            memory_limit: Memory limit (e.g., "128m", "256m")
        
        Returns:
            Dict with:
            - success: bool
            - stdout: str
            - stderr: str
            - exit_code: int
            - error: str (if any)
        """
        if not self.is_available():
            return {
                "success": False,
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "error": "Docker sandbox not available"
            }
        
        try:
            # Create temporary directory for code
            with tempfile.TemporaryDirectory() as tmpdir:
                code_file = Path(tmpdir) / "test_code.py"
                
                # Write code to file
                full_code = code
                if test_code:
                    full_code += f"\n\n# Test code\n{test_code}"
                
                code_file.write_text(full_code)
                
                # Run in Docker container
                try:
                    container = self.client.containers.run(
                        image="python:3.10-slim",
                        command=["python", "/code/test_code.py"],
                        volumes={tmpdir: {'bind': '/code', 'mode': 'ro'}},
                        mem_limit=memory_limit,
                        network_disabled=True,  # No network access
                        remove=True,
                        detach=False,
                        stdout=True,
                        stderr=True,
                        timeout=timeout,
                        # Security options
                        cap_drop=["ALL"],
                        security_opt=["no-new-privileges"],
                        read_only=True,
                        tmpfs={'/tmp': 'size=10M,mode=1777'}
                    )
                    
                    return {
                        "success": True,
                        "stdout": container.decode('utf-8') if isinstance(container, bytes) else str(container),
                        "stderr": "",
                        "exit_code": 0,
                        "error": None
                    }
                
                except docker.errors.ContainerError as e:
                    return {
                        "success": False,
                        "stdout": e.stdout.decode('utf-8') if e.stdout else "",
                        "stderr": e.stderr.decode('utf-8') if e.stderr else "",
                        "exit_code": e.exit_status,
                        "error": f"Code execution failed: {str(e)}"
                    }
                
                except Exception as e:
                    return {
                        "success": False,
                        "stdout": "",
                        "stderr": "",
                        "exit_code": -1,
                        "error": f"Container error: {str(e)}"
                    }
        
        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "error": str(e)
            }
    
    def test_javascript_code(
        self,
        code: str,
        test_code: Optional[str] = None,
        timeout: int = 10,
        memory_limit: str = "128m"
    ) -> Dict[str, Any]:
        """Execute JavaScript/Node.js code in a sandboxed environment.
        
        Args:
            code: JavaScript code to execute
            test_code: Optional test code to run after main code
            timeout: Maximum execution time in seconds
            memory_limit: Memory limit
        
        Returns:
            Dict with execution results
        """
        if not self.is_available():
            return {
                "success": False,
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "error": "Docker sandbox not available"
            }
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                code_file = Path(tmpdir) / "test_code.js"
                
                full_code = code
                if test_code:
                    full_code += f"\n\n// Test code\n{test_code}"
                
                code_file.write_text(full_code)
                
                try:
                    container = self.client.containers.run(
                        image="node:18-alpine",
                        command=["node", "/code/test_code.js"],
                        volumes={tmpdir: {'bind': '/code', 'mode': 'ro'}},
                        mem_limit=memory_limit,
                        network_disabled=True,
                        remove=True,
                        detach=False,
                        stdout=True,
                        stderr=True,
                        timeout=timeout,
                        cap_drop=["ALL"],
                        security_opt=["no-new-privileges"],
                        read_only=True,
                        tmpfs={'/tmp': 'size=10M,mode=1777'}
                    )
                    
                    return {
                        "success": True,
                        "stdout": container.decode('utf-8') if isinstance(container, bytes) else str(container),
                        "stderr": "",
                        "exit_code": 0,
                        "error": None
                    }
                
                except docker.errors.ContainerError as e:
                    return {
                        "success": False,
                        "stdout": e.stdout.decode('utf-8') if e.stdout else "",
                        "stderr": e.stderr.decode('utf-8') if e.stderr else "",
                        "exit_code": e.exit_status,
                        "error": f"Code execution failed: {str(e)}"
                    }
                
                except Exception as e:
                    return {
                        "success": False,
                        "stdout": "",
                        "stderr": "",
                        "exit_code": -1,
                        "error": f"Container error: {str(e)}"
                    }
        
        except Exception as e:
            logger.error(f"JavaScript sandbox execution failed: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "error": str(e)
            }
    
    def test_auto_fix(
        self,
        original_code: str,
        fixed_code: str,
        language: str = "python",
        test_cases: Optional[str] = None
    ) -> Dict[str, Any]:
        """Test if an auto-fix actually works without breaking the code.
        
        Args:
            original_code: Original code before fix
            fixed_code: Code after applying auto-fix
            language: Programming language (python, javascript, etc.)
            test_cases: Optional test cases to verify behavior
        
        Returns:
            Dict with:
            - original_result: Execution result of original code
            - fixed_result: Execution result of fixed code
            - is_improvement: bool (True if fix doesn't break code)
            - recommendation: str
        """
        if not self.is_available():
            return {
                "original_result": None,
                "fixed_result": None,
                "is_improvement": False,
                "recommendation": "Cannot test - Docker sandbox unavailable"
            }
        
        # Execute original code
        if language == "python":
            original_result = self.test_python_code(original_code, test_cases)
            fixed_result = self.test_python_code(fixed_code, test_cases)
        elif language in ["javascript", "typescript"]:
            original_result = self.test_javascript_code(original_code, test_cases)
            fixed_result = self.test_javascript_code(fixed_code, test_cases)
        else:
            return {
                "original_result": None,
                "fixed_result": None,
                "is_improvement": False,
                "recommendation": f"Language '{language}' not supported for sandbox testing"
            }
        
        # Analyze results
        original_works = original_result.get("success", False) or original_result.get("exit_code") == 0
        fixed_works = fixed_result.get("success", False) or fixed_result.get("exit_code") == 0
        
        if not original_works and fixed_works:
            recommendation = "✅ APPLY FIX - Original code has errors, fix resolves them"
            is_improvement = True
        elif original_works and fixed_works:
            recommendation = "✅ SAFE TO APPLY - Both versions work, fix doesn't break functionality"
            is_improvement = True
        elif original_works and not fixed_works:
            recommendation = "❌ DO NOT APPLY - Fix introduces new errors"
            is_improvement = False
        else:
            recommendation = "⚠️ REVIEW NEEDED - Both original and fixed code have issues"
            is_improvement = False
        
        return {
            "original_result": original_result,
            "fixed_result": fixed_result,
            "is_improvement": is_improvement,
            "recommendation": recommendation
        }
    
    def pull_images(self):
        """Pre-pull Docker images for faster execution"""
        if not self.is_available():
            return
        
        images = ["python:3.10-slim", "node:18-alpine"]
        for image in images:
            try:
                logger.info(f"Pulling Docker image: {image}")
                self.client.images.pull(image)
                logger.info(f"Successfully pulled {image}")
            except Exception as e:
                logger.warning(f"Failed to pull {image}: {e}")


# Singleton instance
_code_sandbox = None

def get_code_sandbox() -> CodeSandbox:
    """Get or create the code sandbox singleton"""
    global _code_sandbox
    if _code_sandbox is None:
        _code_sandbox = CodeSandbox()
    return _code_sandbox
