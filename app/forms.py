from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField


class CheckForm(FlaskForm):
    proxy = TextAreaField("Enter proxy")
    api_key = TextAreaField("Enter key")
    submit = SubmitField("Check it")
