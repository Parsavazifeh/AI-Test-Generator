import pytest

def test_greet_typical_case():
    assert greet("Alice") == "Hello, Alice!"

def test_greet_empty_input():
    assert greet("") == "Hello, !"

def test_greet_none_input():
    with pytest.raises(TypeError):
        greet(None)

def test_greet_invalid_type():
    with pytest.raises(TypeError):
        greet(123)

def test_greet_long_name():
    long_name = "A" * 100
    assert greet(long_name) == f"Hello, {long_name}!"