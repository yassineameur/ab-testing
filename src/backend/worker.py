from datetime import datetime, timedelta

from src.backend.config import Config
from src.backend.database_service import DatabaseConnection
from src.backend.db_models import ABTest, TestStatuses
from src.backend.utils.db_utils import get_test_populations, get_tests_to_compute, get_kpis_by_test
from src.backend.khi_two_test import KhiTwoTest
from src.backend.kpi import get_kpi_by_name
from src.backend.logger import getLogger

logger = getLogger().bind(context="worker")


def compute_kpis_for_test(
    pumpkin_connection: DatabaseConnection,
    datalake_connection: DatabaseConnection,
    test: ABTest,
):

    results_per_kpis = {}
    test_populations = get_test_populations(
        datalake_connection=datalake_connection, test_id=test.id
    )
    for kpi_in_db in get_kpis_by_test(datalake_connection, test.id):
        kpi = get_kpi_by_name(kpi_in_db.name)
        if kpi is None:
            logger.error("KPI not found", name=kpi_in_db.name)
            break
        results_per_kpis[kpi.name] = kpi.compute_values_for_populations(
            pumpkin_connection=pumpkin_connection,
            datalake_connection=datalake_connection,
            populations=test_populations,
            start_date=test.start_date,
            end_date=test.end_date,
        )

    return results_per_kpis


def _run_test(
    datalake_connection: DatabaseConnection,
    pumpkin_connection: DatabaseConnection,
    test: ABTest,
) -> None:

    # try:
    kpis_results = compute_kpis_for_test(
        pumpkin_connection=pumpkin_connection,
        datalake_connection=datalake_connection,
        test=test,
    )

    for kpi_name, kpi_result_per_population in kpis_results.items():
        KhiTwoTest.compute_test(
            datalake_engine=datalake_connection.engine,
            test=test,
            kpi_name=kpi_name,
            kpi_res_per_population=kpi_result_per_population,
        )
        logger.info(
            "Kpi results is computed", test_name=test.name, kpi_name=kpi_name
        )

    update_test_status(datalake_connection, test.id)
    logger.info("Test status is updated", test_name=test.name)
    # pylint: disable=W0703
    # except Exception as e:
        # logger.error("Error while computing a test", test=test.name, exc=str(e))


def update_test_status(datalake_connection: DatabaseConnection, test_id: int):

    session = datalake_connection.session_maker()
    test = session.query(ABTest).filter_by(id=test_id).first()

    if datetime.utcnow() >= test.end_date + timedelta(
        minutes=Config().worker_frequency
    ):
        test.status = TestStatuses.completed
    else:
        test.status = TestStatuses.in_progress
    session.commit()


def run_tests(
    datalake_connection: DatabaseConnection, pumpkin_connection: DatabaseConnection
) -> None:

    # Find tests that not yet started
    tests = get_tests_to_compute(datalake_connection)

    # We filter
    for test in tests:
        _run_test(
            datalake_connection=datalake_connection,
            pumpkin_connection=pumpkin_connection,
            test=test,
        )
