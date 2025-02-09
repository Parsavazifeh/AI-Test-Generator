import pytest
from core.test_generator.validation import validate_test_case

@pytest.mark.parametrize("test_code, expected", [
    # ✅ Valid test cases
    ("def test_valid():\n    assert 1 + 1 == 2", True),
    ("import pytest\n\ndef test_something():\n    with pytest.raises(ValueError):\n        raise ValueError()", True),

    # ❌ Invalid test cases (SyntaxError)
    ("def test_invalid():\n    assert 1 + ", False),
    ("def test_missing_colon()\n    pass", False),
])
def test_validate_test_case(test_code, expected):
    """Test validation function for generated test cases."""
    assert validate_test_case(test_code) == expected