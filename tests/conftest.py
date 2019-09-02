import pytest
from src.backend.database_service import get_datalake_connection
from src.backend.db_models import PATT_SCHEMA_NAME, initialize_db
from src.webapp import create_app


@pytest.fixture
def database():

    datalake_connection = get_datalake_connection()

    datalake_connection.engine.execute(
        "DROP SCHEMA IF EXISTS {} CASCADE".format(PATT_SCHEMA_NAME)
    )
    initialize_db(datalake_connection.engine)

    return datalake_connection


@pytest.fixture
def app():

    app = create_app()
    yield app
