from datetime import datetime
from os import environ
from typing import Any

from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from sqlalchemy import (
    engine,
    Table,
    Column,
    Integer,
    String,
    DateTime,
    Index,
    Float,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.backend.config import Config

Base = declarative_base()  # type: Any


class Roles:

    admin = "admin"
    testor = "ab_testor"


class UserStatuses:

    confirmed = "Confirmed"
    pending = "Pending"


class TestStatuses:

    completed = "Completed"
    in_progress = "In progress"
    new = "New"


PATT_SCHEMA_NAME = environ.get("PATT_DB_SCHEMA_NAME", "backend")


class ABTest(Base):

    __tablename__ = "ab_test"
    __table_args__ = (
        Index("ix_name_1", "name", unique=True),
        {"schema": PATT_SCHEMA_NAME},



    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    populations = relationship("TestedUser", backref="test", lazy=True)
    results = relationship("ABTestResult", backref="test", lazy=True)
    kpis = relationship("KPI", backref="test", lazy=True)


class ABTestResult(Base):

    __tablename__ = "test_result"
    __table_args__ = (
        Index(
            "ix_test_result",
            "test_id",
            "kpi_name",
            "first_population_name",
            "second_population_name",
            unique=True,
        ),
        {"schema": PATT_SCHEMA_NAME},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(
        Integer, ForeignKey("{}.ab_test.id".format(PATT_SCHEMA_NAME)), nullable=False
    )
    test_type = Column(String, nullable=False)
    kpi_name = Column(String, nullable=False)
    first_population_name = Column(String, nullable=False)
    second_population_name = Column(String, nullable=False)
    first_population_avg = Column(Float, nullable=False)
    second_population_avg = Column(Float, nullable=False)
    pvalue = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def upsert_test_results(
        cls,
        db_engine: engine,
        test_id: int,
        test_type: str,
        kpi_name: str,
        first_population_name: str,
        second_population_name: str,
        first_population_avg: float,
        second_population_avg: float,
        pvalue: float,
        updated_at: datetime,
    ):
        query = """
                INSERT INTO {0}.{1} 
                    (test_id, test_type, kpi_name, first_population_name, second_population_name, first_population_avg, second_population_avg, pvalue, updated_at) 
                    VALUES ({2}, '{3}', '{4}', '{5}', '{6}', {7}, {8}, {9}, '{10}') ON CONFLICT (test_id, kpi_name, first_population_name, second_population_name) DO UPDATE SET 
                        test_id = excluded.test_id,
                        test_type = excluded.test_type,
                        kpi_name = excluded.kpi_name,
                        first_population_name = excluded.first_population_name,
                        second_population_name = excluded.second_population_name,
                        first_population_avg = excluded.first_population_avg,
                        second_population_avg = excluded.second_population_avg,
                        pvalue = excluded.pvalue,
                        updated_at = excluded.updated_at
            """.format(
            PATT_SCHEMA_NAME,
            cls.__tablename__,
            test_id,
            test_type,
            kpi_name,
            first_population_name,
            second_population_name,
            first_population_avg,
            second_population_avg,
            pvalue,
            updated_at,
        )

        db_engine.execute(query)


class KPI(Base):

    __tablename__ = "kpi"
    __table_args__ = (
        Index("ix_kpi_result", "test_id", "name", unique=True),
        {"schema": PATT_SCHEMA_NAME},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(
        Integer, ForeignKey("{}.ab_test.id".format(PATT_SCHEMA_NAME)), nullable=False
    )
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def upsert_test_results(
        cls,
        db_engine: engine,
        test_id: int,
        test_type: str,
        kpi_name: str,
        first_population_name: str,
        second_population_name: str,
        first_population_avg: float,
        second_population_avg: float,
        pvalue: float,
        updated_at: datetime,
    ):
        query = """
                INSERT INTO {0}.{1} 
                    (test_id, test_type, kpi_name, first_population_name, second_population_name, first_population_avg, second_population_avg, pvalue, updated_at) 
                    VALUES ({2}, '{3}', '{4}', '{5}', '{6}', {7}, {8}, {9}, '{10}') ON CONFLICT (test_id, kpi_name, first_population_name, second_population_name) DO UPDATE SET 
                        test_id = excluded.test_id,
                        test_type = excluded.test_type,
                        kpi_name = excluded.kpi_name,
                        first_population_name = excluded.first_population_name,
                        second_population_name = excluded.second_population_name,
                        first_population_avg = excluded.first_population_avg,
                        second_population_avg = excluded.second_population_avg,
                        pvalue = excluded.pvalue,
                        updated_at = excluded.updated_at
            """.format(
            PATT_SCHEMA_NAME,
            cls.__tablename__,
            test_id,
            test_type,
            kpi_name,
            first_population_name,
            second_population_name,
            first_population_avg,
            second_population_avg,
            pvalue,
            updated_at,
        )

        db_engine.execute(query)


class TestedUser(Base):
    """
    This models one user in a population
    """

    __tablename__ = "tested_user"
    __table_args__ = (
        Index(
            "ix_population_name_user_id",
            "user_id",
            "test_id",
            "population_name",
            unique=True,
        ),
        {"schema": PATT_SCHEMA_NAME},
    )
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    test_id = Column(
        Integer, ForeignKey("{}.ab_test.id".format(PATT_SCHEMA_NAME)), nullable=False
    )
    population_name = Column(String)
    created_at = Column(String, nullable=False, default=datetime.utcnow)

    @classmethod
    def get_users_ids_from_db(
        cls, db_engine: engine.Engine, test_name: str, population_name: str
    ):
        query = """
                SELECT user_id FROM {}.{} WHERE  test_name = '{}' AND population_name = '{}'
            """.format(
            PATT_SCHEMA_NAME, cls.__tablename__, test_name, population_name
        )
        return db_engine.execute(query)


class PattUser(Base, UserMixin):

    __tablename__ = "patt_user"
    __table_args__ = (
        Index("ix_email", "email", unique=True),
        {"schema": PATT_SCHEMA_NAME},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    status = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    def upsert_admin(cls, db_engine: engine.Engine) -> None:

        db_config = Config()
        query = """
                INSERT INTO {0}.{1} 
                    (email, password, status, role, created_at, updated_at)
                    VALUES ('{2}', '{3}', '{4}', '{5}', '{6}', '{7}')
                ON CONFLICT (email)
                DO UPDATE SET 
                    email = excluded.email,
                    password = excluded.password,
                    status = excluded.status,
                    role = excluded.role,
                    updated_at = excluded.updated_at
                    """.format(
            PATT_SCHEMA_NAME,
            cls.__tablename__,
            db_config.admin_email,
            Bcrypt().generate_password_hash(db_config.admin_password).decode("utf-8"),
            UserStatuses.confirmed,
            Roles.admin,
            datetime.utcnow(),
            datetime.utcnow(),
        )
        db_engine.execute(query)

    @classmethod
    def update_status(
        cls, db_engine: engine, email: str, status: str, updated_at: datetime
    ):
        query = """
                UPDATE {}.{} 
                    SET status = '{}', updated_at = '{}'
                    WHERE email = '{}'
            """.format(
            PATT_SCHEMA_NAME, cls.__tablename__, status, updated_at, email
        )

        db_engine.execute(query)

    @classmethod
    def delete(cls, db_engine: engine.Engine, email: str):

        query = """
        DELETE FROM {}.{} WHERE email = '{}'
        """.format(
            PATT_SCHEMA_NAME, cls.__tablename__, email
        )

        db_engine.execute(query)


def _create_table_if_not_exists(
    db_engine: engine.Engine, table_model_instance: Table
) -> None:
    """
    Creates each datalake table if doesn't exist
    :param db_engine:
    :param table_model_instance:
    """
    table_name = table_model_instance.__tablename__

    if not db_engine.has_table(table_name, schema=PATT_SCHEMA_NAME):
        table_model_instance.__table__.create(bind=db_engine)


def _create_schema(db_engine: engine.Engine):
    db_engine.execute("CREATE SCHEMA IF NOT EXISTS {};".format(PATT_SCHEMA_NAME))


def _create_missing_tables(db_engine: engine.Engine) -> None:
    """
    Creates all the tables that does not yet exists
    :param db_engine:
    :return: None
    """

    tables_instances = [
        ABTest(),
        TestedUser(),
        ABTestResult(),
        KPI(),
        PattUser(),
    ]

    for table_instance in tables_instances:
        _create_table_if_not_exists(db_engine, table_instance)

    # We finally insert the admin

    PattUser.upsert_admin(db_engine)


def initialize_db(db_engine: engine.Engine):

    _create_schema(db_engine)
    _create_missing_tables(db_engine)
