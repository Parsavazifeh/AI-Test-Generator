import pytest

def test_add_typical_case():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-5, 10) == 5

def test_add_zero():
    assert add(0, 0) == 0

def test_add_large_numbers():
    assert add(1000000, 2000000) == 3000000

def test_add_invalid_type():
    with pytest.raises(TypeError):
        add("2", 3)

def test_add_none_values():
    with pytest.raises(TypeError):
        add(None, None)

def test_add_empty_inputs():
    with pytest.raises(TypeError):
        add()

def test_add_mixed_types():
    with pytest.raises(TypeError):
        add(3, "4")