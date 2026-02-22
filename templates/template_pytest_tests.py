"""
Template — Tests Pytest Standard
Structure de tests pytest avec fixtures et assertions
"""

import json

import pytest


# Fixtures communes
@pytest.fixture
def sample_data():
    """Fixture fournissant des données de test"""
    return {"id": 1, "name": "Test Item", "value": 42}


@pytest.fixture
def temp_file(tmp_path):
    """Fixture créant un fichier temporaire"""
    file_path = tmp_path / "test_file.json"
    data = {"test": "data"}
    with open(file_path, "w") as f:
        json.dump(data, f)
    return file_path


# Tests de base
def test_simple_assertion():
    """Test avec assertion simple"""
    assert 1 + 1 == 2


def test_string_operations():
    """Test des opérations sur les chaînes"""
    text = "Hello World"
    assert text.lower() == "hello world"
    assert text.upper() == "HELLO WORLD"
    assert len(text) == 11


def test_list_operations():
    """Test des opérations sur les listes"""
    items = [1, 2, 3, 4, 5]
    assert len(items) == 5
    assert 3 in items
    assert items[0] == 1
    assert items[-1] == 5


def test_dict_operations():
    """Test des opérations sur les dictionnaires"""
    data = {"key": "value", "number": 42}
    assert "key" in data
    assert data["key"] == "value"
    assert data.get("missing", "default") == "default"


# Tests avec fixtures
def test_with_sample_data(sample_data):
    """Test utilisant une fixture"""
    assert sample_data["id"] == 1
    assert sample_data["name"] == "Test Item"
    assert sample_data["value"] == 42


def test_with_temp_file(temp_file):
    """Test utilisant un fichier temporaire"""
    assert temp_file.exists()

    with open(temp_file) as f:
        data = json.load(f)

    assert data["test"] == "data"


# Tests d'exceptions
def test_exception_raised():
    """Test vérifiant qu'une exception est levée"""
    with pytest.raises(ZeroDivisionError):
        result = 1 / 0


def test_exception_message():
    """Test vérifiant le message d'une exception"""
    with pytest.raises(ValueError, match="invalid literal"):
        int("not a number")


# Tests paramétrés
@pytest.mark.parametrize(
    "input,expected",
    [
        (1, 2),
        (2, 4),
        (3, 6),
        (4, 8),
    ],
)
def test_double(input, expected):
    """Test paramétré avec plusieurs cas"""
    assert input * 2 == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("hello", "HELLO"),
        ("world", "WORLD"),
        ("Python", "PYTHON"),
    ],
)
def test_uppercase(text, expected):
    """Test paramétré pour la conversion en majuscules"""
    assert text.upper() == expected


# Tests de classes
class TestCalculator:
    """Groupe de tests pour une calculatrice"""

    def test_add(self):
        """Test de l'addition"""
        assert 2 + 2 == 4

    def test_subtract(self):
        """Test de la soustraction"""
        assert 5 - 3 == 2

    def test_multiply(self):
        """Test de la multiplication"""
        assert 3 * 4 == 12

    def test_divide(self):
        """Test de la division"""
        assert 10 / 2 == 5

    def test_divide_by_zero(self):
        """Test de la division par zéro"""
        with pytest.raises(ZeroDivisionError):
            result = 10 / 0


# Tests avec setup/teardown
class TestWithSetup:
    """Tests avec méthodes setup et teardown"""

    def setup_method(self):
        """Exécuté avant chaque test"""
        self.data = [1, 2, 3]

    def teardown_method(self):
        """Exécuté après chaque test"""
        self.data = None

    def test_data_exists(self):
        """Test que les données existent"""
        assert self.data is not None
        assert len(self.data) == 3

    def test_data_content(self):
        """Test du contenu des données"""
        assert self.data[0] == 1
        assert self.data[-1] == 3


# Tests marqués (skip, xfail, etc.)
@pytest.mark.skip(reason="Test non implémenté")
def test_not_implemented():
    """Test à implémenter plus tard"""
    pass


@pytest.mark.skipif(True, reason="Condition non remplie")
def test_conditional_skip():
    """Test sauté conditionnellement"""
    pass


@pytest.mark.xfail(reason="Bug connu")
def test_known_bug():
    """Test qui échoue de manière attendue"""
    assert False


# Tests de performance
def test_performance():
    """Test vérifiant la performance"""
    import time

    start = time.time()

    # Opération à tester
    result = sum(range(1000000))

    duration = time.time() - start
    assert duration < 1.0  # Doit prendre moins d'1 seconde
    assert result == 499999500000
