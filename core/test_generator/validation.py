import ast
import re
import importlib
from typing import Tuple, List, Dict
import pytest
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class TestValidator:
    def __init__(self, test_code: str, function_info: Dict = None):
        self.test_code = test_code
        self.function_info = function_info
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_all(self) -> Tuple[bool, List[str]]:
        """Run all validation checks in sequence"""
        checks = [
            self.validate_syntax,
            self.validate_security,
            self.validate_pytest_structure,
            self.validate_test_naming,
            self.validate_assertions,
            self.validate_mocking,
            self.validate_dependencies
        ]
        
        for check in checks:
            if not check():
                logger.error(f"Validation failed in {check.__name__}")
        
        return len(self.errors) == 0, self.errors + self.warnings

    def validate_syntax(self) -> bool:
        """Check for basic Python syntax errors"""
        try:
            ast.parse(self.test_code)
            return True
        except SyntaxError as e:
            self.errors.append(f"Syntax error: {str(e)}")
            return False

    def validate_security(self) -> bool:
        """Check for dangerous patterns/imports"""
        dangerous_patterns = [
            (r'(os\.system|subprocess\.run|eval|exec)\s*\(', "Dangerous system call detected"),
            (r'__import__\s*\(', "Unsafe import detected"),
            (r'(open|file)\s*\(', "Potential file operation detected")
        ]
        
        safe = True
        tree = ast.parse(self.test_code)
        
        # AST-based checks
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ['os', 'subprocess', 'sys']:
                        self.warnings.append(f"Potentially risky import: {alias.name}")
            
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'id') and node.func.id in ['eval', 'exec']:
                    self.errors.append(f"Dangerous function call: {node.func.id}")
                    safe = False

        # Regex pattern checks
        for pattern, message in dangerous_patterns:
            if re.search(pattern, self.test_code):
                self.errors.append(message)
                safe = False
                
        return safe

    def validate_pytest_structure(self) -> bool:
        """Verify pytest conventions are followed"""
        required_imports = ['pytest', 'unittest.mock', 'mock']
        has_imports = any(imp in self.test_code for imp in required_imports)
        
        if not has_imports:
            self.warnings.append("Missing pytest or mock imports")
            
        return True  # Not fatal, just warning

    def validate_test_naming(self) -> bool:
        """Ensure test functions follow naming conventions"""
        tree = ast.parse(self.test_code)
        test_functions = [
            node for node in ast.walk(tree) 
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')
        ]
        
        if not test_functions:
            self.errors.append("No test functions found (missing 'test_' prefix)")
            return False
            
        return True

    def validate_assertions(self) -> bool:
        """Check for presence of valid assertions"""
        assertion_patterns = [
            r'assert\s+',
            r'pytest\.raises\(\)',
            r'unittest\.TestCase\.assert'
        ]
        
        if not any(re.search(pattern, self.test_code) for pattern in assertion_patterns):
            self.errors.append("No valid assertions found in test code")
            return False
            
        return True

    def validate_mocking(self) -> bool:
        """Check if required mocks are present"""
        if self.function_info and any(arg['type'] == 'Callable' for arg in self.function_info['args']):
            mock_patterns = [
                r'@patch\b',
                r'Mock\(',
                r'mocker\.patch\b'
            ]
            
            if not any(re.search(pattern, self.test_code) for pattern in mock_patterns):
                self.warnings.append("Callable argument detected but no mocks found")
                
        return True  # Warning only

    def validate_dependencies(self) -> bool:
        """Check if required dependencies are imported"""
        try:
            tree = ast.parse(self.test_code)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)
                    
            # Check for existence of imported modules
            for imp in imports:
                try:
                    importlib.import_module(imp)
                except ImportError:
                    self.errors.append(f"Missing dependency: {imp}")
                    return False
                    
            return True
        except Exception as e:
            self.errors.append(f"Dependency check failed: {str(e)}")
            return False

def validate_test_case(test_code: str, function_info: Dict = None) -> Tuple[bool, List[str]]:
    """Public validation interface"""
    validator = TestValidator(test_code, function_info)
    return validator.validate_all()

def log_validation_errors(test_code: str, errors: List[str]):
    """Log failed validations to the error log"""
    log_file = Path("data/failed_tests.log")
    error_msg = "\n".join(errors)
    
    with log_file.open("a") as f:
        f.write(f"\n{'='*40}\nValidation Errors:\n{error_msg}\nTest Code:\n{test_code}\n")