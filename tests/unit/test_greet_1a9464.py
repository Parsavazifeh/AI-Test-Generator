import pytest

def test_valid_name():
    assert greet("Alice") == "Hello, Alice!"

def test_empty_name():
    assert greet("") == "Hello, !"

def test_none_name():
    assert greet(None) == "Hello, None!"

def test_invalid_type():
    with pytest.raises(TypeError):
        greet(123)

def test_long_name():
    assert greet("Supercalifragilisticexpialidocious") == "Hello, Supercalifragilisticexpialidocious!"

def test_special_characters_name():
    assert greet("@#$%^&") == "Hello, @#$%^&"

def test_unicode_name():
    assert greet("नमस्ते") == "Hello, नमस्ते"