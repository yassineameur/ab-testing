from flask import Flask

from src.backend.database_service import DatabaseConnection
from src.frontend.routing import (
    general_routing,
    tests_routing,
    user_routing,
)


def add_routes(app: Flask, datalake_connection: DatabaseConnection):

    tests_routing.add_routes(app, datalake_connection)
    user_routing.add_routes(app, datalake_connection)
    general_routing.add_routes(app, datalake_connection)
