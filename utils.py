from decimal import Decimal


def amount_with_spaces(amount: Decimal) -> str:
    """Format a decimal number with spaces as thousands separators."""
    return f"{amount:,.2f}".replace(",", " ")


def amount_with_sign_and_space(amount: Decimal) -> str:
    """Format a decimal number with a sign and space as thousands separators."""
    sign = "+" if amount >= 0 else "-"
    return f"{sign} {amount_with_spaces(abs(amount))}"
