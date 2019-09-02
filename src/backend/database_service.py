from typing import NamedTuple

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from src.backend.config import Config
from src.backend.logger import getLogger

logger = getLogger()


class DatabaseConnection(NamedTuple):
    """
    This class models a database connection
    """

    engine: Engine
    session_maker: sessionmaker


def get_datalake_connection() -> DatabaseConnection:

    engine = create_engine(Config().datalake_url)
    session_maker = sessionmaker(bind=engine)
    logger.info("Database connection to datalake is established !")

    return DatabaseConnection(engine=engine, session_maker=session_maker)


def get_pumpkin_connection() -> DatabaseConnection:

    engine = create_engine(Config().pumpkin_url)
    session_maker = sessionmaker(bind=engine)
    logger.info("Database connection to pumpkin prod is established !")

    return DatabaseConnection(engine=engine, session_maker=session_maker)
