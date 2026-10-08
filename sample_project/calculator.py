def add(a, b):
    """Return the sum of two numbers."""
    return a + b


def subtract(a, b):
    """Return the difference between two numbers."""
    return a - b


def multiply(a, b):
    """Return the product of a number."""
    return a * b


def divide(a, b):
    """Return the result of dividing a by b."""
    if b == 0:
        raise ValueError('Division by zero is not allowed')
    return a / b


def square(a):
    """Return the square of a number."""
    return a * a