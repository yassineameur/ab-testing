from os import environ
from typing import NamedTuple


class Config(NamedTuple):

    datalake_url: str = environ.get(
        "DATALAKE_DB_URL", "postgresql://postgres@localhost:5432/datalake"
    )
    pumpkin_url: str = environ.get(
        "PUMPKIN_DB_URL", """postgresql://postgres@localhost:5432/pumpkin"""
    )

    admin_email: str = environ.get("ADMIN_EMAIL", "bi@pumpkin-app.com")
    admin_password: str = environ.get("ADMIN_PASSWORD", "fake_password")

    worker_frequency: int = int(
        environ.get("WORKER_FREQUENCY", "1")
    )  # Worker frequency in seconds
