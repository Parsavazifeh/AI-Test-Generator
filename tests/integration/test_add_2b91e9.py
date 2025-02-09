import pytest

def add(a, b):
    return a + b

def test_add_typical_case():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-5, -7) == -12

def test_add_zero():
    assert add(0, 0) == 0

def test_add_empty_input():
    with pytest.raises(TypeError):
        add()

def test_add_one_none_value():
    with pytest.raises(TypeError):
        add(5, None)

def test_add_invalid_types():
    with pytest.raises(TypeError):
        add("5", 3)
    with pytest.raises(TypeError):
        add(5, "3")
    with pytest.raises(TypeError):
        add("5", "3")