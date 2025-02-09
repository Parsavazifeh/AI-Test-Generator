import pytest

def get_element(key):
    return {
        'name': 'Alice',
        'age': 30,
        'city': 'New York'
    }.get(key, None)

def test_valid_key():
    assert get_element('name') == 'Alice'
    assert get_element('age') == 30
    assert get_element('city') == 'New York'

def test_invalid_key():
    assert get_element('gender') is None

def test_empty_key():
    assert get_element('') is None

def test_none_key():
    assert get_element(None) is None

def test_invalid_type():
    with pytest.raises(AttributeError):
        get_element(123)