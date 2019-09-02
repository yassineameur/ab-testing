import pandas as pd
from flask import Flask, render_template, url_for, flash, redirect, abort
from flask_login import login_required

from src.backend.database_service import DatabaseConnection
from src.backend.db_models import ABTest, KPI, ABTestResult, TestStatuses
from src.backend.utils.db_utils import (
    read_populations_file,
    insert_new_test,
    get_all_tests,
    delete_test_by_id,
)
from src.frontend.forms import TestCreationForm, TestUpdateForm


def add_routes(app: Flask, datalake_connection: DatabaseConnection):
    @app.route("/tests/all")
    @login_required
    # pylint: disable=W0612
    def tests():
        return render_template(
            "tests.html", title="Tests", tests=get_all_tests(datalake_connection)
        )

    @app.route("/tests/new", methods=["GET", "POST"])
    @login_required
    # pylint: disable=W0612
    def new_test():

        form = TestCreationForm()
        if form.validate_on_submit():

            try:
                populations_df = pd.read_excel(io=form.populations_file.data.stream)

                ab_test = ABTest(
                    name=form.name.data,
                    description=form.description.data,
                    start_date=form.start_date.data,
                    end_date=form.end_date.data,
                    status=TestStatuses.new,
                )
                populations = read_populations_file(
                    test_id=ab_test.id, populations_df=populations_df
                )

                insert_new_test(
                    datalake_connection=datalake_connection,
                    ab_test=ab_test,
                    populations=populations,
                    kpis=form.kpis.data,
                )
            # pylint: disable=W0703
            except Exception as e:
                flash(str(e), category="danger")
                return render_template("create_test.html", title="New tests", form=form)

            flash("Your test has been added !", category="success")
            return redirect(url_for("tests"))

        return render_template("create_test.html", title="New tests", form=form)

    @app.route("/tests/edit/<test_id>", methods=["GET", "POST"])
    @login_required
    # pylint: disable=W0612
    def edit_test(test_id):

        session = datalake_connection.session_maker()

        test = session.query(ABTest).filter_by(id=test_id).first()
        if test is None:
            abort(status=404)

        kpis = [kpi.name for kpi in test.kpis]
        form = TestUpdateForm(
            name=test.name,
            description=test.description,
            start_date=test.start_date,
            end_date=test.end_date,
            kpis=kpis,
        )
        if form.validate_on_submit():
            try:
                test.description = form.description.data
                test.name = form.name.data
                test.start_date = form.start_date.data
                test.end_date = form.end_date.data

                # Delete old kpis and insert new ones
                current_kpis = set(kpi.name for kpi in test.kpis)
                new_kpis = set(kpi_name for kpi_name in form.kpis.data)

                kpis_to_add = new_kpis - current_kpis
                kpis_to_delete = current_kpis - new_kpis
                for kpi_to_delete in kpis_to_delete:
                    session.query(KPI).filter_by(
                        name=kpi_to_delete, test_id=test_id
                    ).delete()
                    session.query(ABTestResult).filter_by(
                        kpi_name=kpi_to_delete, test_id=test_id
                    ).delete()
                for kpi_to_add in kpis_to_add:
                    kpi = KPI(test_id=test.id, name=kpi_to_add)
                    session.add(kpi)

                session.commit()
            # pylint: disable=W0703
            except Exception as e:
                flash(str(e), category="danger")
                return render_template("update_test.html", title="New tests", form=form)

            flash("{} has been updated !".format(test.name), category="success")
            return redirect(url_for("tests"))

        return render_template("update_test.html", title="New tests", form=form)

    @app.route("/tests/delete/<test_id>", methods=["POST"])
    @login_required
    # pylint: disable=W0612
    def delete_test(test_id):

        session = datalake_connection.session_maker()
        test = session.query(ABTest).filter_by(id=test_id).first()

        if test is None:
            abort(status=404)

        delete_test_by_id(datalake_connection=datalake_connection, test_id=test_id)

        return redirect(url_for("tests"))

    @app.route("/test_results/<test_id>", methods=["GET"])
    @login_required
    # pylint: disable=W0612
    def get_test_results(test_id):
        session = datalake_connection.session_maker()
        results = session.query(ABTestResult).filter_by(test_id=test_id).all()
        return render_template("results.html", title="Test results", results=results)
