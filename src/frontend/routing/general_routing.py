from flask import Flask, render_template, url_for, flash, redirect, request
from flask_login import login_user as flask_login_user, current_user, logout_user

from src.backend.auth_lib import insert_new_user, login_user
from src.backend.database_service import DatabaseConnection
from src.frontend.forms import RegistrationForm, LoginForm


def add_routes(app: Flask, datalake_connection: DatabaseConnection):
    @app.route("/")
    @app.route("/home")
    # pylint: disable=W0612
    def home():
        return redirect(url_for("tests"))

    @app.route("/about")
    # pylint: disable=W0612
    def about():
        return render_template("about.html", title="About")

    @app.route("/register", methods=["GET", "POST"])
    # pylint: disable=W0612
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        form = RegistrationForm()
        if form.validate_on_submit():
            register_message = insert_new_user(
                datalake_connection=datalake_connection,
                email=form.email.data,
                password=form.password.data,
            )
            flash(register_message.message, register_message.category)
            return redirect(url_for("home"))

        return render_template("register.html", title="Register", form=form)

    @app.route("/login", methods=["GET", "POST"])
    # pylint: disable=W0612
    def login():

        if current_user.is_authenticated:
            return redirect(url_for("home"))

        form = LoginForm()
        if form.validate_on_submit():
            login_message = login_user(
                datalake_connection, form.email.data, form.password.data
            )
            flash(login_message.message, login_message.category)
            if login_message.category == "success":
                flask_login_user(user=login_message.user, remember=form.remember.data)
                next_page = request.args.get("next")
                if next_page:
                    return redirect(next_page)
                return redirect(url_for("tests"))
        return render_template("login.html", title="Login", form=form)

    @app.route("/logout")
    # pylint: disable=W0612
    def logout():

        logout_user()
        return redirect(url_for("home"))
