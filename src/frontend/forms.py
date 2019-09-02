from datetime import date, timedelta

import pandas as pd
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    TextAreaField,
    DateField,
    SelectMultipleField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    ValidationError,
)

from src.backend.kpi import get_kpis


class RegistrationForm(FlaskForm):

    email = StringField("Email", validators=[DataRequired(), Email()])

    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])

    confirm_password = PasswordField(
        "Confirm password", validators=[DataRequired(), EqualTo(fieldname="password")]
    )

    submit = SubmitField("Submit")


class ResetPasswordForm(FlaskForm):

    current_password = PasswordField("Current password", validators=[DataRequired()])
    new_password = PasswordField(
        "New password", validators=[DataRequired(), Length(min=6)]
    )
    confirm_new_password = PasswordField(
        "Confirm new password",
        validators=[DataRequired(), EqualTo(fieldname="new_password")],
    )

    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])

    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])

    remember = BooleanField("Remember me")
    login = SubmitField("Login")


class TestForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])

    start_date = DateField(
        "Start date", validators=[DataRequired()], default=date.today()
    )

    end_date = DateField(
        "End date",
        validators=[DataRequired()],
        default=date.today() + timedelta(days=7),
    )

    kpis = SelectMultipleField(
        "kpis",
        choices=[(kpi.name, kpi.name) for kpi in get_kpis()],
        validators=[DataRequired()],
    )


class TestCreationForm(TestForm):

    populations_file = FileField(
        "Populations file (.xlsx)", validators=[DataRequired(), FileAllowed(["xlsx"])]
    )

    submit = SubmitField("Add test")

    # pylint: disable=R0201
    def validate_populations_file(self, populations_file):

        populations_df = pd.read_excel(io=populations_file.data.stream)
        columns = list(populations_df.columns)
        expected_columns = ["user_id", "population_name"]
        for expected_column in expected_columns:
            if expected_column not in columns:
                raise ValidationError(
                    "Expected column named {}".format(expected_column)
                )
        populations_df = populations_df[expected_columns]

        populations_number = populations_df["population_name"].nunique()

        expected_populations_number = 2
        if populations_number != expected_populations_number:
            raise ValidationError(
                "You have given {} populations, we accept {} populations".format(
                    populations_number, expected_populations_number
                )
            )


class TestUpdateForm(TestForm):

    submit = SubmitField("Update test")
