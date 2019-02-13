from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class RequestCapacityForm(FlaskForm):
    pub_key = StringField('Your PubKey', validators=[DataRequired()])
    twitter_username = StringField('Twitter Username (optional)')
    email_address = StringField('E-mail Address (optional)')
    fee_rate = SelectField('Fee Rate', choices=[('test', 'TEST')])
    capacity = SelectField('Capacity', choices=[('test', 'TEST')])
    request_capacity = SubmitField('Request Capacity')
