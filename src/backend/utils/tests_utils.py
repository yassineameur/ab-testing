from datetime import datetime

import pandas as pd
from sqlalchemy.engine import Engine

from src.backend.logger import getLogger

logger = getLogger().bind(context="utils")


def _flatten_transactions(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    We flatten transactions so that we have one user per row
    """

    transactions_df = transactions_df.copy(deep=False)
    logger.info("Flattening transactions")
    debited_transactions_df = transactions_df[["owner_id", "debited_person_id"]]
    debited_transactions_df.rename(
        {"debited_person_id": "user_id"}, axis=1, inplace=True
    )
    credited_transactions_df = transactions_df[["owner_id", "credited_person_id"]]
    credited_transactions_df.rename(
        {"credited_person_id": "user_id"}, axis=1, inplace=True
    )

    return pd.concat([credited_transactions_df, debited_transactions_df])


def _get_valid_transactions(
    pumpkin_engine: Engine, start_date: datetime, end_date: datetime
) -> pd.DataFrame:

    query = """
        SELECT owner_id, credited_person_id, debited_person_id FROM abstract_transaction
        WHERE created_at BETWEEN '{}' AND '{}'
        AND transaction_status = 'SUCCEEDED'
        AND visibility <> 4
        AND credited_person_id <>  debited_person_id
        AND credited_person_id IS NOT NULL AND debited_person_id IS NOT NULL
        AND discr IN ('transfer', 'guest_transfer', 'qr_code_transfer', 'charge', 'guest_charge')
    """.format(
        start_date, end_date
    )
    logger.info("Getting transactions", start_date=start_date, end_date=end_date)
    transactions_df = pd.read_sql_query(query, pumpkin_engine.engine)
    return _flatten_transactions(transactions_df)


def get_valid_transactions_per_user(
    pumpkin_engine: Engine,
    ownership_is_must: bool,
    start_date: datetime,
    end_date: datetime,
) -> pd.DataFrame:

    valid_transactions_df = _get_valid_transactions(
        pumpkin_engine=pumpkin_engine, start_date=start_date, end_date=end_date
    )
    if ownership_is_must:
        valid_transactions_df = valid_transactions_df[
            valid_transactions_df["user_id"] == valid_transactions_df["owner_id"]
        ]

    if valid_transactions_df.shape[0] == 0:
        logger.info("No transactions have been found")
        return pd.DataFrame(data=[], columns=["user_id", "transactions_number"])

    logger.info("Computing transactions number per user")
    return (
        valid_transactions_df[["user_id"]]
        .groupby(["user_id"])
        .size()
        .reset_index(name="transactions_number")
    )


def get_population_transactions(
    pumpkin_engine: Engine,
    users_ids,
    ownership_is_must: bool,
    start_date: datetime,
    end_date: datetime,
):

    valid_transactions_df = get_valid_transactions_per_user(
        pumpkin_engine=pumpkin_engine,
        ownership_is_must=ownership_is_must,
        start_date=start_date,
        end_date=end_date,
    )

    # We merge data with population users
    users_df = pd.DataFrame(data=users_ids, columns=["user_id"])
    logger.info("Merging transactions with population users")
    population_result = pd.merge(
        left=users_df, right=valid_transactions_df, on=["user_id"], how="left"
    )
    population_result.fillna(0, inplace=True)
    logger.info("Transactions are got for users")

    return population_result
