from src.calculator import Calculator

def main() -> None:
    """Fonction principale pour l'application calculatrice en ligne de commande."""
    while True:
        print("\nOpérations disponibles: +, -, *, / (ou 'q' pour quitter)")
        operation = input("Choisissez une opération: ")

        if operation.lower() == 'q':
            print("Au revoir !")
            break

        if operation not in ['+', '-', '*', '/']:
            print("Erreur: Opération invalide. Veuillez choisir parmi +, -, *, /.")
            continue

        try:
            num1 = input("Entrez le premier nombre: ")
            num2 = input("Entrez le deuxième nombre: ")

            result = 0.0
            if operation == '+':
                result = Calculator.add(num1, num2)
            elif operation == '-':
                result = Calculator.subtract(num1, num2)
            elif operation == '*':
                result = Calculator.multiply(num1, num2)
            elif operation == '/':
                result = Calculator.divide(num1, num2)

            print(f"Résultat: {result}")

        except ValueError as e:
            print(f"Erreur d'entrée: {e}")
        except ZeroDivisionError as e:
            print(f"Erreur mathématique: {e}")
        except Exception as e:
            print(f"Une erreur inattendue est survenue: {e}")

if __name__ == "__main__":
    main()
