from os import environ
from typing import NamedTuple

from flask import Flask
from flask_login import LoginManager


class App(NamedTuple):

    flask_app: Flask
    login_manager: LoginManager


FLASK_APP = None


def build_app() -> App:

    # pylint: disable=W0603
    global FLASK_APP
    if FLASK_APP is None:

        app = Flask(__name__)
        login_manager = LoginManager(app)
        login_manager.login_view = "login"
        login_manager.login_message_category = "info"

        app.config["SECRET_KEY"] = environ.get(
            "SECRET_KEY", "023af5a0253f5ff468b25fa40fd5d85f"
        )

        FLASK_APP = App(flask_app=app, login_manager=login_manager)

    return FLASK_APP
