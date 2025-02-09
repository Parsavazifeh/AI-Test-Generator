# tests/test_ast_parser.py

import pytest
import os
import ast
from core.code_parser.ast_parser import parse_python_file, extract_function_info, extract_class_info

@pytest.fixture
def sample_file(tmp_path):
    """Fixture to create temporary Python files for testing"""
    def create_sample_file(content):
        file_path = tmp_path / "sample.py"
        file_path.write_text(content)
        return str(file_path)
    return create_sample_file

def test_parse_empty_file(sample_file):
    """Test parsing of an empty Python file"""
    content = ""
    file_path = sample_file(content)
    result = parse_python_file(file_path)
    
    assert result == {"functions": [], "classes": []}

def test_simple_function_parsing(sample_file):
    """Test parsing of a function with basic parameters"""
    content = """
def add(a: int, b: int) -> int:
    \"\"\"Add two numbers\"\"\"
    return a + b
"""
    file_path = sample_file(content)
    result = parse_python_file(file_path)
    
    assert len(result["functions"]) == 1
    func = result["functions"][0]
    assert func["name"] == "add"
    assert [a["name"] for a in func["args"]] == ["a", "b"]
    assert func["return_type"] == "int"
    assert func["docstring"] == "Add two numbers"
    assert func["start_line"] == 2
    assert func["end_line"] == 4

def test_class_with_methods(sample_file):
    """Test parsing of a class with methods"""
    content = """
class Calculator:
    \"\"\"Basic calculator class\"\"\"
    
    def __init__(self, precision: int = 2):
        self.precision = precision
        
    def add(self, a: float, b: float) -> float:
        return round(a + b, self.precision)
"""
    file_path = sample_file(content)
    result = parse_python_file(file_path)
    
    assert len(result["classes"]) == 1
    cls = result["classes"][0]
    assert cls["name"] == "Calculator"
    assert cls["docstring"] == "Basic calculator class"
    assert len(cls["methods"]) == 2
    
    init_method = cls["methods"][0]
    assert init_method["name"] == "__init__"
    assert init_method["args"][1]["name"] == "precision"
    assert init_method["args"][1]["type"] == "int"
    
    add_method = cls["methods"][1]
    assert add_method["return_type"] == "float"

def test_function_with_complex_args(sample_file):
    """Test parsing of complex argument types"""
    content = """
def process_data(
    data: list[dict[str, int]],
    callback: Callable[[int], None],
    *args: str,
    timeout: float = 5.0,
    **kwargs: Any
) -> bool:
    pass
"""
    file_path = sample_file(content)
    result = parse_python_file(file_path)
    
    func = result["functions"][0]
    args = func["args"]
    
    # Check positional arguments
    assert args[0]["name"] == "data"
    assert args[0]["type"] == "list[dict[str, int]]"
    
    assert args[1]["name"] == "callback"
    assert args[1]["type"] == "Callable[[int], None]"
    
    # Check variable positional arguments (*args)
    assert args[2]["name"] == "args"
    assert args[2]["type"] == "str"
    assert args[2].get("is_vararg") is True
    
    # Check keyword argument with default value
    assert args[3]["name"] == "timeout"
    assert args[3]["type"] == "float"
    
    # Check variable keyword arguments (**kwargs)
    assert args[4]["name"] == "kwargs"
    assert args[4]["type"] == "Any"
    assert args[4].get("is_kwarg") is True

def test_error_handling(sample_file):
    """Test parser error handling"""
    # Test invalid file path
    with pytest.raises(FileNotFoundError):
        parse_python_file("non_existent_file.py")
    
    # Test syntax error
    content = "def invalid_syntax("
    file_path = sample_file(content)
    with pytest.raises(SyntaxError) as exc_info:
        parse_python_file(file_path)
    assert "Syntax error" in str(exc_info.value)

def test_decorators_handling(sample_file):
    """Test parsing of decorated functions"""
    content = """
@log_call
@validate_args(int, float)
def calculate(rate: int, amount: float) -> float:
    return rate * amount
"""
    file_path = sample_file(content)
    result = parse_python_file(file_path)
    
    func = result["functions"][0]
    assert func["name"] == "calculate"
    assert len(func["args"]) == 2

# tests/test_ast_parser.py (partial update)

def test_async_function_parsing(sample_file):
    """Test parsing of async functions"""
    content = """
async def fetch_data(url: str) -> dict:
    \"\"\"Fetch data from API\"\"\"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
"""
    file_path = sample_file(content)
    result = parse_python_file(file_path)
    
    assert len(result["functions"]) == 1
    func = result["functions"][0]
    assert func["name"] == "fetch_data"
    assert func["is_async"] is True

def test_class_inheritance(sample_file):
    """Test parsing of class inheritance"""
    content = """
class AdvancedCalculator(Calculator, Loggable):
    pass
"""
    file_path = sample_file(content)
    result = parse_python_file(file_path)
    
    cls = result["classes"][0]
    assert cls["bases"] == ["Calculator", "Loggable"]

def test_type_alias_handling(sample_file):
    """Test parsing of type aliases"""
    content = """
Vector = list[float]

def normalize(v: Vector) -> Vector:
    return [x / max(v) for x in v]
"""
    file_path = sample_file(content)
    result = parse_python_file(file_path)
    
    func = result["functions"][0]
    assert func["args"][0]["type"] == "Vector"