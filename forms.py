from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL, length


class SubmitUrlForm(FlaskForm):
    url = StringField("Enter an https:// URL:", validators=[DataRequired(), URL(), length(max=250)])
    submit = SubmitField("Submit")


class PremiumUrlForm(FlaskForm):
    url = StringField("URL", validators=[DataRequired(), URL(), length(max=250)])
    short_custom_url = StringField("Custom URL", validators=[length(max=20)])
    submit = SubmitField("Submit")



