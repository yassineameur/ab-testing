from datetime import datetime
from typing import List, Dict

import pandas as pd

from src.backend.database_service import DatabaseConnection
from src.backend.db_models import (
    TestedUser,
    ABTest,
    ABTestResult,
    TestStatuses,
    KPI
)
from src.backend.logger import getLogger

logger = getLogger().bind(context="population")


def get_test_by_id(datalake_connection: DatabaseConnection, test_id: int) -> ABTest:

    return (
        datalake_connection.session_maker().query(ABTest).filter_by(id=test_id).first()
    )


def get_kpis_by_test(datalake_connection: DatabaseConnection, test_id: int) -> List[KPI]:

    return datalake_connection.session_maker().query(KPI).filter_by(test_id=test_id).all()


def insert_new_test(
    datalake_connection: DatabaseConnection,
    ab_test: ABTest,
    populations: List[TestedUser],
    kpis: List[str],
):

    session = datalake_connection.session_maker()
    session.add(ab_test)
    session.commit()

    #  We will try now to find the user
    test_in_db = session.query(ABTest).filter_by(name=ab_test.name).first()

    try:
        for population in populations:
            population.test_id = test_in_db.id
            session.add(population)

        for kpi_name in kpis:
            kpi_to_add = KPI(name=kpi_name, test_id=test_in_db.id)
            session.add(kpi_to_add)

        session.commit()
    except Exception as e:
        delete_test_by_id(datalake_connection, ab_test.id)
        raise Exception(
            "An error has occurred when inserting the test: {}".format(str(e))
        )


def read_populations_file(test_id, populations_df: pd.DataFrame) -> List[TestedUser]:

    populations = []
    for _, row_data in populations_df.iterrows():
        population = TestedUser(
            user_id=row_data["user_id"],
            test_id=test_id,
            population_name=row_data["population_name"],
        )
        populations.append(population)

    return populations


def get_all_tests(datalake_connection: DatabaseConnection) -> List[ABTest]:

    return datalake_connection.session_maker().query(ABTest).all()


def get_tests_to_compute(datalake_connection: DatabaseConnection,) -> List[ABTest]:

    return (
        datalake_connection.session_maker()
        .query(ABTest)
        .filter(
            ABTest.start_date <= datetime.utcnow(),
            ABTest.status != TestStatuses.completed,
        )
        .all()
    )


def delete_test_by_id(datalake_connection: DatabaseConnection, test_id: int) -> None:

    session = datalake_connection.session_maker()
    # We start by deleting the test's populations and results

    session.query(TestedUser).filter_by(test_id=test_id).delete()
    session.query(ABTestResult).filter_by(test_id=test_id).delete()
    session.query(KPI).filter_by(test_id=test_id).delete()
    session.query(ABTest).filter_by(id=test_id).delete()

    session.commit()


def get_test_populations(
    datalake_connection: DatabaseConnection, test_id: int
) -> Dict[str, pd.DataFrame]:

    session = datalake_connection.session_maker()

    populations = session.query(TestedUser).filter_by(test_id=test_id).all()
    if not populations:
        return {}

    populations_data = [
        {"name": population.population_name, "user_id": population.user_id}
        for population in populations
    ]
    all_populations_df = pd.DataFrame(data=populations_data)

    return {
        population_name: population_members["user_id"]
        for population_name, population_members in all_populations_df.groupby(["name"])
    }
