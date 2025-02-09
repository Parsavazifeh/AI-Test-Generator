"""
AST (Abstract Syntax Tree) Parser for Python Code

This module extracts detailed information about functions and classes from Python source files.
It provides structured data about function signatures, arguments, return types, docstrings, and class hierarchies.
"""

import ast
import os
from typing import List, Dict, Union, Optional

class ParentAssigner(ast.NodeVisitor):
    """Add parent references to AST nodes"""
    def visit(self, node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            child.parent = node  # type: ignore
            self.visit(child)

def extract_function_info(node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> Dict[str, Union[str, List, None]]:
    """
    Extract function information, including complex argument types and variable arguments.
    """
    def extract_arg_info(arg: ast.arg) -> Dict[str, Optional[str]]:
        """Helper to extract argument name and type annotation"""
        return {
            "name": arg.arg,
            "type": ast.unparse(arg.annotation) if arg.annotation else None
        }

    # Extract positional arguments
    args = [extract_arg_info(arg) for arg in node.args.args]
    
    # Extract variable positional arguments (*args)
    if node.args.vararg:
        args.append({
            "name": node.args.vararg.arg,
            "type": ast.unparse(node.args.vararg.annotation) if node.args.vararg.annotation else None,
            "is_vararg": True
        })
    
    # Extract keyword-only arguments
    for arg in node.args.kwonlyargs:
        args.append(extract_arg_info(arg))
    
    # Extract variable keyword arguments (**kwargs)
    if node.args.kwarg:
        args.append({
            "name": node.args.kwarg.arg,
            "type": ast.unparse(node.args.kwarg.annotation) if node.args.kwarg.annotation else None,
            "is_kwarg": True
        })

    return {
        "name": node.name,
        "args": args,
        "return_type": ast.unparse(node.returns) if node.returns else None,
        "docstring": ast.get_docstring(node),
        "start_line": node.lineno,
        "end_line": node.end_lineno,
        "is_async": isinstance(node, ast.AsyncFunctionDef)
    }

def extract_class_info(node: ast.ClassDef) -> Dict[str, Union[str, List, None]]:
    """
    Extract detailed information from a class definition node.
    
    Args:
        node (ast.ClassDef): AST node representing a class definition
        
    Returns:
        Dictionary containing:
        - name: Class name
        - bases: List of base classes
        - docstring: Class docstring
        - methods: List of class methods
        - start_line: Starting line number
        - end_line: Ending line number
    """
    methods = []
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            methods.append(extract_function_info(item))

    return {
        "name": node.name,
        "bases": [ast.unparse(base) for base in node.bases],
        "docstring": ast.get_docstring(node),
        "methods": methods,
        "start_line": node.lineno,
        "end_line": node.end_lineno
    }

def parse_python_file(file_path: str) -> Dict[str, List]:
    """Main parsing function with parent tracking"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    full_path = os.path.abspath(file_path)

    with open(full_path, "r", encoding="utf-8") as source_file:
        try:
            tree = ast.parse(source_file.read(), filename=full_path)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in {full_path} at line {e.lineno}: {e.msg}") from e

    # Add parent references to all nodes
    ParentAssigner().visit(tree)

    analysis_result = {"functions": [], "classes": []}

    for node in ast.walk(tree):
        # Handle both regular and async functions
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check if parent is a ClassDef
            if not isinstance(getattr(node, 'parent', None), ast.ClassDef):
                analysis_result["functions"].append(extract_function_info(node))
        
        # Handle class definitions
        elif isinstance(node, ast.ClassDef):
            methods = [
                extract_function_info(child) 
                for child in node.body 
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            analysis_result["classes"].append({
                "name": node.name,
                "bases": [ast.unparse(base) for base in node.bases],
                "docstring": ast.get_docstring(node),
                "methods": methods,
                "start_line": node.lineno,
                "end_line": node.end_lineno
            })

    return analysis_result