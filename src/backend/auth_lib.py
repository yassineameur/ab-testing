from datetime import datetime
from typing import NamedTuple

from flask_bcrypt import Bcrypt
from sqlalchemy.engine import Engine

from src.backend.database_service import DatabaseConnection, get_datalake_connection
from src.backend.db_models import PattUser, Roles
from src.frontend.flask_app import build_app

# pylint: disable=R0903
class UserStatus:
    confirmed = "Confirmed"
    pending = "Pending"


class UserAuthMessage(NamedTuple):

    category: str
    message: str
    user: object


login_manager = build_app().login_manager


@login_manager.user_loader
def load_user(user_id):

    session = get_datalake_connection().session_maker()
    user = session.query(PattUser).filter_by(id=int(user_id)).first()
    return user


def insert_new_user(
    datalake_connection: DatabaseConnection, email: str, password: str
) -> UserAuthMessage:
    try:
        password = Bcrypt().generate_password_hash(password).decode("utf-8")
        user = PattUser(
            email=email,
            password=password,
            status=UserStatus.pending,
            role=Roles.testor,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session = datalake_connection.session_maker()
        session.add(user)
        session.commit()
        return UserAuthMessage(
            message="Account creation demand for '{}' has been sent to admin, "
            "he will contact you soon !".format(email),
            category="success",
            user={},
        )
    # pylint: disable=W0702
    except:
        return UserAuthMessage(
            message="En error has occurred: Check that user is not yet created!",
            category="danger",
            user={},
        )


def confirm_user(db_engine: Engine, email: str):

    PattUser.update_status(
        db_engine=db_engine,
        email=email,
        status=UserStatus.confirmed,
        updated_at=datetime.utcnow(),
    )


def login_user(datalake_connection: DatabaseConnection, email: str, password: str):

    session = datalake_connection.session_maker()
    user = session.query(PattUser).filter_by(email=email).first()
    if user is not None:

        if Bcrypt().check_password_hash(user.password, password):
            if user.status == UserStatus.confirmed:
                return UserAuthMessage(
                    message="Login successful", category="success", user=user
                )

            return UserAuthMessage(
                message="Please wait for admin validation", category="danger", user=None
            )

        return UserAuthMessage(message="Bad password", category="danger", user=None)

    return UserAuthMessage(message="User does not exist", category="danger", user=None)


def update_user_password(
    datalake_connection: DatabaseConnection, email: str, new_password: str
):

    new_password = Bcrypt().generate_password_hash(new_password).decode("utf-8")

    session = datalake_connection.session_maker()
    user = session.query(PattUser).filter_by(email=email).first()
    user.password = new_password
    session.commit()
