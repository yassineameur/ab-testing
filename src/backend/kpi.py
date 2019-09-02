from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional

import numpy as np
import pandas as pd

from src.backend.database_service import DatabaseConnection
from src.backend.logger import getLogger
from src.backend.utils.tests_utils import get_population_transactions

logger = getLogger().bind(context="KPI")


class AbstractKPI(ABC):
    def __init__(self, name: str):

        self.name = name

    @abstractmethod
    def compute_values_for_population(
        self,
        pumpkin_connection: DatabaseConnection,
        datalake_connection: DatabaseConnection,
        users_ids: np.array,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:
        """
        :param pumpkin_connection:
        :param datalake_connection:
        :param users_ids:
        :param start_date:
        :param end_date:
        :return: kpis value for population members
        """

    def compute_values_for_populations(
        self,
        pumpkin_connection: DatabaseConnection,
        datalake_connection: DatabaseConnection,
        populations: Dict[str, pd.DataFrame],
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, pd.DataFrame]:
        """
        :param pumpkin_connection:
        :param datalake_connection:
        :param populations:
        :param start_date:
        :param end_date:
        :return: kpi values for all population
        """
        populations_results = {}
        for population_name, users_ids in populations.items():
            populations_results[population_name] = self.compute_values_for_population(
                pumpkin_connection, datalake_connection, users_ids, start_date, end_date
            )
        return populations_results


class TransactionsNumberKPI(AbstractKPI):
    def __init__(self, name: str, ownership_is_must: bool):

        super().__init__(name=name)
        self.ownership_is_must = ownership_is_must

    def compute_values_for_population(
        self,
        pumpkin_connection: DatabaseConnection,
        datalake_connection: DatabaseConnection,
        users_ids: np.array,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:

        transactions_per_user_df = get_population_transactions(
            pumpkin_engine=pumpkin_connection.engine,
            users_ids=users_ids,
            ownership_is_must=self.ownership_is_must,
            start_date=start_date,
            end_date=end_date,
        )

        transactions_per_user_df.rename(
            {"transactions_number": "value"}, axis=1, inplace=True
        )
        return transactions_per_user_df


class TransactionsNumberWithOwnership(TransactionsNumberKPI):
    def __init__(self):

        super().__init__(name="Owned transactions number", ownership_is_must=True)


class AllTransactionsNumber(TransactionsNumberKPI):
    def __init__(self):
        super().__init__(name="Transactions number", ownership_is_must=False)


class ActivationKPI(AbstractKPI):
    def __init__(self, name: str, ownership_is_must: bool):
        """
        :param ownership_is_must: The transaction has to be owned to be considered as activation
        """
        super().__init__(name=name)
        self.ownership_is_must = ownership_is_must

    def compute_values_for_population(
        self,
        pumpkin_connection: DatabaseConnection,
        datalake_connection: DatabaseConnection,
        users_ids: np.array,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:
        population_transactions_df = get_population_transactions(
            pumpkin_engine=pumpkin_connection.engine,
            users_ids=users_ids,
            ownership_is_must=self.ownership_is_must,
            start_date=start_date,
            end_date=end_date,
        )
        population_transactions_df["value"] = (
            population_transactions_df["transactions_number"] > 0
        )

        return population_transactions_df[["user_id", "value"]]


class ActivationWithOwnership(ActivationKPI):
    def __init__(self):

        super().__init__(name="Owned activation", ownership_is_must=True)


class SimpleActivation(ActivationKPI):
    def __init__(self):
        super().__init__(name="Simple activation", ownership_is_must=False)


def get_kpis() -> List[AbstractKPI]:

    return [
        TransactionsNumberWithOwnership(),
        AllTransactionsNumber(),
        ActivationWithOwnership(),
        SimpleActivation(),
    ]


def get_kpi_by_name(name: str) -> Optional[AbstractKPI]:

    for kpi in get_kpis():
        if kpi.name == name:
            return kpi

    return None
