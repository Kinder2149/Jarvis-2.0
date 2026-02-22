"""
Template — Calculatrice Python
Module de calcul avec gestion des erreurs et tests pytest
"""


class Calculator:
    """Calculatrice avec opérations de base et gestion d'erreurs"""

    @staticmethod
    def add(a: float, b: float) -> float:
        """Addition de deux nombres"""
        return a + b

    @staticmethod
    def subtract(a: float, b: float) -> float:
        """Soustraction de deux nombres"""
        return a - b

    @staticmethod
    def multiply(a: float, b: float) -> float:
        """Multiplication de deux nombres"""
        return a * b

    @staticmethod
    def divide(a: float, b: float) -> float:
        """
        Division de deux nombres

        Raises:
            ZeroDivisionError: Si b est égal à 0
        """
        if b == 0:
            raise ZeroDivisionError("Division par zéro impossible")
        return a / b


def main():
    """Interface CLI pour la calculatrice"""
    calc = Calculator()

    print("=== Calculatrice Python ===")
    print("1. Addition")
    print("2. Soustraction")
    print("3. Multiplication")
    print("4. Division")
    print("0. Quitter")

    while True:
        try:
            choice = input("\nChoisissez une opération (0-4): ").strip()

            if choice == "0":
                print("Au revoir!")
                break

            if choice not in ["1", "2", "3", "4"]:
                print("Choix invalide. Veuillez choisir entre 0 et 4.")
                continue

            a = float(input("Premier nombre: "))
            b = float(input("Deuxième nombre: "))

            if choice == "1":
                result = calc.add(a, b)
                print(f"Résultat: {a} + {b} = {result}")
            elif choice == "2":
                result = calc.subtract(a, b)
                print(f"Résultat: {a} - {b} = {result}")
            elif choice == "3":
                result = calc.multiply(a, b)
                print(f"Résultat: {a} * {b} = {result}")
            elif choice == "4":
                try:
                    result = calc.divide(a, b)
                    print(f"Résultat: {a} / {b} = {result}")
                except ZeroDivisionError as e:
                    print(f"Erreur: {e}")

        except ValueError:
            print("Erreur: Veuillez entrer des nombres valides")
        except KeyboardInterrupt:
            print("\nInterruption détectée. Au revoir!")
            break


if __name__ == "__main__":
    main()
