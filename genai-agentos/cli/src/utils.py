from functools import wraps
from typing import Optional
from uuid import UUID

import typer
from src.exceptions import APIError, DependencyError, UnAuthorizedException
from src.log import render_error
from src.http import HTTPRepository


def validate_uuid(value: str, field_name: str) -> Optional[str]:
    try:
        return str(UUID(value))
    except ValueError:
        render_error(f"{field_name} is not a valid uuid - {value}")
        return


def cli_error_renderer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (APIError, DependencyError, OSError, UnAuthorizedException) as e:
            render_error(str(e))
            return typer.Exit(1)

    return wrapper

def load_jwt(http_repo: HTTPRepository) -> str:
    # Return dummy token for local dev
    return "dev-token"
