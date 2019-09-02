from time import sleep

from src.backend.config import Config
from src.backend.database_service import get_datalake_connection, get_pumpkin_connection
from src.backend.db_models import initialize_db
from src.backend.worker import run_tests

if __name__ == "__main__":

    initialize_db(db_engine=get_datalake_connection().engine)

    while True:

        datalake_connection = get_datalake_connection()
        pumpkin_connection = get_pumpkin_connection()
        run_tests(
            datalake_connection=datalake_connection,
            pumpkin_connection=pumpkin_connection,
        )

        sleep(60 * Config().worker_frequency)
