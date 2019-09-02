from os import environ

from src.backend.database_service import get_datalake_connection
from src.backend.db_models import initialize_db
from src.frontend.flask_app import build_app
from src.frontend.routing import all_routes


def create_app():
    # We start by initializing database
    datalake_connection = get_datalake_connection()
    initialize_db(datalake_connection.engine)
    patt_app = build_app()
    all_routes.add_routes(patt_app.flask_app, datalake_connection)

    return patt_app.flask_app


if __name__ == "__main__" and environ.get("DEBUG") == "1":
    debug_app = create_app()
    debug_app.run(debug=True)
