"""SymPy-based mathematical equivalence checking engine."""

from sympy import simplify, sympify, SympifyError


class SympyEngine:
    """Uses SymPy to check mathematical equivalence between expressions."""

    @staticmethod
    def check_equivalence(expr1: str, expr2: str) -> dict:
        """Check if two mathematical expressions are equivalent.

        Returns:
            dict with keys: equivalent (bool), simplified_diff (str), error (str|None)
        """
        try:
            parsed_1 = sympify(expr1)
            parsed_2 = sympify(expr2)
            diff = simplify(parsed_1 - parsed_2)
            is_equivalent = diff == 0
            return {
                "equivalent": is_equivalent,
                "simplified_diff": str(diff),
                "error": None,
            }
        except SympifyError as e:
            return {
                "equivalent": False,
                "simplified_diff": "",
                "error": f"Failed to parse expression: {e}",
            }

    @staticmethod
    def check_form(expr: str, expected_form: str) -> dict:
        """Check if expression matches the expected form (factored, expanded, etc.). TODO: Phase 2."""
        raise NotImplementedError
