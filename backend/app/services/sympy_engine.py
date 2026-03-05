"""SymPy-based mathematical equivalence and form checking engine."""

import re

from sympy import expand, simplify, SympifyError
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

# Transformations that handle implicit multiplication: (x+2)(x+3) -> (x+2)*(x+3)
_TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


def _parse(expr_str: str):
    """Parse expression string with implicit multiplication support."""
    return parse_expr(expr_str, transformations=_TRANSFORMATIONS)


class SympyEngine:
    """Uses SymPy to check mathematical equivalence and form correctness."""

    @staticmethod
    def _clean_latex(expr: str) -> str:
        """Convert common LaTeX notation to SymPy-parseable format."""
        s = expr.strip()
        # Remove $ delimiters
        s = s.replace("$", "")
        # Remove \text{...}
        s = re.sub(r"\\text\{[^}]*\}", "", s)
        # \frac{a}{b} -> (a)/(b)
        s = re.sub(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"(\1)/(\2)", s)
        # \sqrt{a} -> sqrt(a)
        s = re.sub(r"\\sqrt\{([^}]*)\}", r"sqrt(\1)", s)
        # \pi -> pi
        s = s.replace("\\pi", "pi")
        # \cdot -> *
        s = s.replace("\\cdot", "*")
        # Remove remaining backslash commands (e.g. \left, \right)
        s = re.sub(r"\\(left|right|,|;|quad|qquad)", "", s)
        # ^ for exponents (SymPy uses **)
        s = s.replace("^", "**")
        return s.strip()

    @staticmethod
    def check_equivalence(expr1: str, expr2: str) -> dict:
        """Check if two mathematical expressions are equivalent.

        Returns:
            dict with keys: equivalent (bool), simplified_diff (str), error (str|None)
        """
        try:
            clean1 = SympyEngine._clean_latex(expr1)
            clean2 = SympyEngine._clean_latex(expr2)
            parsed_1 = _parse(clean1)
            parsed_2 = _parse(clean2)
            diff = simplify(parsed_1 - parsed_2)
            is_equivalent = diff == 0
            return {
                "equivalent": is_equivalent,
                "simplified_diff": str(diff),
                "error": None,
            }
        except (SympifyError, SyntaxError, TypeError, ValueError) as e:
            return {
                "equivalent": False,
                "simplified_diff": "",
                "error": f"Failed to parse expression: {e}",
            }

    @staticmethod
    def check_form(expr: str, expected_form: str) -> dict:
        """Check if expression matches the expected form.

        Returns:
            dict with keys: matches (bool), reason (str), error (str|None)
        """
        try:
            clean = SympyEngine._clean_latex(expr)
            parsed = _parse(clean)

            if expected_form == "numeric":
                matches = parsed.is_number is True
                reason = "Expression is numeric" if matches else "Expression is not a pure number"
                return {"matches": matches, "reason": reason, "error": None}

            if expected_form == "expanded":
                expanded = expand(parsed)
                matches = (expanded - parsed) == 0
                reason = (
                    "Expression is in expanded form"
                    if matches
                    else "Expression is not fully expanded"
                )
                return {"matches": matches, "reason": reason, "error": None}

            if expected_form == "factored":
                expanded = expand(parsed)
                # If expanding changes the expression, it was in factored form
                matches = (expanded - parsed) != 0
                reason = (
                    "Expression is in factored form"
                    if matches
                    else "Expression is already expanded, not factored"
                )
                return {"matches": matches, "reason": reason, "error": None}

            if expected_form == "simplified":
                return {
                    "matches": True,
                    "reason": "Simplified form accepted",
                    "error": None,
                }

            if expected_form == "proof":
                return {
                    "matches": False,
                    "reason": "Proof requires LLM evaluation",
                    "error": None,
                }

            return {
                "matches": True,
                "reason": f"Unknown form '{expected_form}', accepting",
                "error": None,
            }

        except (SympifyError, SyntaxError, TypeError, ValueError) as e:
            return {
                "matches": False,
                "reason": "",
                "error": f"Failed to parse expression: {e}",
            }
