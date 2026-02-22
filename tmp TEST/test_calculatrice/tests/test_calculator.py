import pytest
from src.calculator import Calculator

def test_add_valid_inputs():
    """Teste l'addition avec des entrées valides."""
    assert Calculator.add(5, 3) == 8
    assert Calculator.add(-1, 1) == 0
    assert Calculator.add(1.5, 2.5) == 4.0
    assert Calculator.add("5", "3") == 8.0

def test_subtract_valid_inputs():
    """Teste la soustraction avec des entrées valides."""
    assert Calculator.subtract(5, 3) == 2
    assert Calculator.subtract(-1, 1) == -2
    assert Calculator.subtract(5.5, 1.5) == 4.0
    assert Calculator.subtract("10", "3") == 7.0

def test_multiply_valid_inputs():
    """Teste la multiplication avec des entrées valides."""
    assert Calculator.multiply(5, 3) == 15
    assert Calculator.multiply(-2, 4) == -8
    assert Calculator.multiply(1.5, 2.0) == 3.0
    assert Calculator.multiply("5", "3") == 15.0

def test_divide_valid_inputs():
    """Teste la division avec des entrées valides."""
    assert Calculator.divide(10, 2) == 5
    assert Calculator.divide(-10, 2) == -5
    assert Calculator.divide(5, 2.5) == 2.0
    assert Calculator.divide("10", "4") == 2.5

def test_divide_by_zero():
    """Teste que la division par zéro lève une ZeroDivisionError."""
    with pytest.raises(ZeroDivisionError):
        Calculator.divide(10, 0)

def test_add_invalid_input():
    """Teste que l'addition avec une entrée non numérique lève une ValueError."""
    with pytest.raises(ValueError):
        Calculator.add('a', 5)
    with pytest.raises(ValueError):
        Calculator.add(5, 'b')

def test_subtract_invalid_input():
    """Teste que la soustraction avec une entrée non numérique lève une ValueError."""
    with pytest.raises(ValueError):
        Calculator.subtract('a', 5)
    with pytest.raises(ValueError):
        Calculator.subtract(5, 'b')

def test_multiply_invalid_input():
    """Teste que la multiplication avec une entrée non numérique lève une ValueError."""
    with pytest.raises(ValueError):
        Calculator.multiply('a', 5)
    with pytest.raises(ValueError):
        Calculator.multiply(5, 'b')

def test_divide_invalid_input():
    """Teste que la division avec une entrée non numérique lève une ValueError."""
    with pytest.raises(ValueError):
        Calculator.divide('a', 5)
    with pytest.raises(ValueError):
        Calculator.divide(5, 'b')
