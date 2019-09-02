from flask import Flask, render_template, url_for, redirect, abort, flash
from flask_login import current_user, login_required

from src.backend.auth_lib import login_user, update_user_password
from src.backend.database_service import DatabaseConnection
from src.backend.db_models import PattUser, UserStatuses, Roles
from src.frontend.forms import ResetPasswordForm


def add_routes(app: Flask, datalake_connection: DatabaseConnection):
    @app.route("/users", methods=["GET"])
    @login_required
    # pylint: disable=W0612
    def get_users():

        session = datalake_connection.session_maker()
        users = session.query(PattUser).all()

        return render_template("users.html", title="Users management", users=users)

    @app.route("/users/<user_id>", methods=["GET", "POST"])
    @login_required
    # pylint: disable=W0612
    def confirm_user(user_id):

        if current_user.role != Roles.admin:
            abort(403)

        session = datalake_connection.session_maker()
        user = session.query(PattUser).filter_by(id=user_id).first()
        user.status = UserStatuses.confirmed
        session.commit()
        return redirect(url_for("get_users"))

    @app.route("/users/delete/<user_id>", methods=["GET", "POST"])
    @login_required
    # pylint: disable=W0612
    def delete_user(user_id):
        if current_user.role != Roles.admin:
            abort(403)
        session = datalake_connection.session_maker()
        session.query(PattUser).filter_by(id=user_id).delete()
        session.commit()
        return redirect(url_for("get_users"))

    @app.route("/users/reset_password", methods=["GET", "POST"])
    @login_required
    # pylint: disable=W0612
    def reset_password():

        email = current_user.email
        form = ResetPasswordForm()
        if form.validate_on_submit():
            # We check the current password
            login_result = login_user(
                datalake_connection, email, form.current_password.data
            )
            if login_result.category == "success":
                # update password
                update_user_password(datalake_connection, email, form.new_password.data)
                flash("Password has been updated", category="success")
                return redirect(url_for("get_users"))

            # error message
            flash("Current password is bad", category="danger")

        return render_template("reset_password.html", form=form, title="Reset password")
