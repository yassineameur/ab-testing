import math
from datetime import datetime
from typing import Dict

import numpy as np
import pandas as pd
from scipy import stats
from sqlalchemy.engine import Engine

from src.backend.db_models import ABTestResult, ABTest
from src.backend.logger import getLogger

logger = getLogger().bind(context="Test computing")


class KhiTwoTest:
    @classmethod
    def _get_total_std(cls, serie_1: np.array, serie_2: np.array) -> float:
        return math.sqrt(
            (
                (len(serie_1) - 1) * serie_1.std() ** 2
                + (len(serie_2) - 1) * serie_2.std() ** 2
            )
            / (len(serie_1) + len(serie_2) - 2)
        )

    @classmethod
    def _compute_p_value(cls, serie_1: np.array, serie_2: np.array) -> float:

        total_std = cls._get_total_std(serie_1, serie_2)

        stat = (serie_1.mean() - serie_2.mean()) / (
            total_std * math.sqrt(1 / len(serie_1) + 1 / len(serie_2))
        )

        pvalue = stats.norm.cdf(stat)
        if np.isnan(pvalue):
            return 1.0
        return pvalue

    @classmethod
    def compute_test(
        cls,
        datalake_engine: Engine,
        test: ABTest,
        kpi_name: str,
        kpi_res_per_population: Dict[str, pd.DataFrame],
    ):

        populations_names = list(kpi_res_per_population.keys())

        # For the moment, we accept only two populations for khi 2 tests
        assert len(populations_names) == 2

        serie_1 = kpi_res_per_population[populations_names[0]]["value"]
        serie_2 = kpi_res_per_population[populations_names[1]]["value"]

        pvalue = cls._compute_p_value(serie_1, serie_2)
        logger.info(
            "Pvalue computed",
            test_name=test.name,
            type="khi2",
            kpi_name=kpi_name,
            value=pvalue,
        )

        ABTestResult.upsert_test_results(
            db_engine=datalake_engine,
            test_id=test.id,
            test_type="khi2",
            kpi_name=kpi_name,
            first_population_name=populations_names[0],
            second_population_name=populations_names[1],
            first_population_avg=serie_1.mean(),
            second_population_avg=serie_2.mean(),
            pvalue=pvalue,
            updated_at=datetime.utcnow(),
        )

        logger.info(
            "Test result inserted",
            test_name=test.name,
            type="khi2",
            kpi_name=kpi_name,
            value=pvalue,
        )
