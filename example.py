"""
A simple example Python file for testing AI-based test case generation.
"""

def add(a: int, b: int) -> int:
    """
    Return the sum of a and b.

    Args:
        a (int): The first number.
        b (int): The second number.

    Returns:
        int: The sum of a and b.
    """
    return a + b

class Greeter:
    """
    A simple class to greet a user.
    """
    def greet(self, name: str) -> str:
        """
        Return a greeting for the given name.

        Args:
            name (str): The name of the person to greet.

        Returns:
            str: A greeting message.
        """
        return f"Hello, {name}!"