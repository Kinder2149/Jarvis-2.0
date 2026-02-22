import typing

class Calculator:
    """
    Fournit des méthodes statiques pour des opérations arithmétiques de base.
    """

    @staticmethod
    def add(a: typing.Any, b: typing.Any) -> float:
        """
        Tente de convertir les entrées en float et retourne leur somme.

        Args:
            a: Le premier nombre.
            b: Le deuxième nombre.

        Returns:
            La somme de a et b.

        Raises:
            ValueError: Si a ou b ne peuvent pas être convertis en float.
        """
        try:
            num_a = float(a)
            num_b = float(b)
            return num_a + num_b
        except (ValueError, TypeError):
            raise ValueError("Les deux entrées doivent être des nombres valides.")

    @staticmethod
    def subtract(a: typing.Any, b: typing.Any) -> float:
        """
        Tente de convertir les entrées en float et retourne leur différence.

        Args:
            a: Le premier nombre.
            b: Le deuxième nombre.

        Returns:
            La différence entre a et b.

        Raises:
            ValueError: Si a ou b ne peuvent pas être convertis en float.
        """
        try:
            num_a = float(a)
            num_b = float(b)
            return num_a - num_b
        except (ValueError, TypeError):
            raise ValueError("Les deux entrées doivent être des nombres valides.")

    @staticmethod
    def multiply(a: typing.Any, b: typing.Any) -> float:
        """
        Tente de convertir les entrées en float et retourne leur produit.

        Args:
            a: Le premier nombre.
            b: Le deuxième nombre.

        Returns:
            Le produit de a et b.

        Raises:
            ValueError: Si a ou b ne peuvent pas être convertis en float.
        """
        try:
            num_a = float(a)
            num_b = float(b)
            return num_a * num_b
        except (ValueError, TypeError):
            raise ValueError("Les deux entrées doivent être des nombres valides.")

    @staticmethod
    def divide(a: typing.Any, b: typing.Any) -> float:
        """
        Tente de convertir les entrées en float et retourne leur quotient.

        Args:
            a: Le numérateur.
            b: Le dénominateur.

        Returns:
            Le quotient de a par b.

        Raises:
            ValueError: Si a ou b ne peuvent pas être convertis en float.
            ZeroDivisionError: Si b est égal à zéro.
        """
        try:
            num_a = float(a)
            num_b = float(b)
            if num_b == 0:
                raise ZeroDivisionError("Division par zéro impossible.")
            return num_a / num_b
        except (ValueError, TypeError):
            raise ValueError("Les deux entrées doivent être des nombres valides.")
