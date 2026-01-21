import functools
from collections.abc import Callable
from decimal import Decimal
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def handle_service_exception(service_name: str) -> Callable[[F], F]:
    """
    Decorator to handle exceptions in service run() methods.

    Args:
        service_name: The name of the service for logging purposes
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            try:
                return func(*args, **kwargs)
            except Exception as e:
                from logger import db_logger, main_logger  # noqa: PLC0415
                from services.chat import get_chat_service  # noqa: PLC0415

                # Use appropriate logger based on service name
                logger = db_logger if "account" in service_name.lower() else main_logger

                logger.critical(
                    f"Error in {service_name}: {e}",
                    stack_info=True,
                    exc_info=True,
                )
                get_chat_service().notify_management(
                    text=f"Error in {service_name}",
                    exception=e,
                )
                raise

        return wrapper  # type: ignore[return-value]

    return decorator


def amount_with_spaces(amount: Decimal) -> str:
    """Format a decimal number with spaces as thousands separators."""
    return f"{amount:,.2f}".replace(",", " ")


def amount_with_sign_and_space(amount: Decimal) -> str:
    """Format a decimal number with a sign and space as thousands separators."""
    sign = "+" if amount >= 0 else "-"
    return f"{sign} {amount_with_spaces(abs(amount))}"


def amount_with_sign(amount: Decimal) -> str:
    """Format a decimal number with a sign as thousands separators."""
    sign = "+" if amount >= 0 else "-"
    return f"{sign} {abs(amount):.2f}"
