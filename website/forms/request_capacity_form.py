from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class RequestCapacityForm(FlaskForm):
    pub_key = StringField('Your PubKey', validators=[DataRequired()])
    twitter_username = StringField('Twitter Username (Optional)')
    email_address = StringField('E-mail Address (Optional)')
    transaction_fee_rate = SelectField('Average Channel Opening Speed')
    capacity = SelectField('Capacity')
    capacity_fee_rate = SelectField('Minimum Time Open')
    request_capacity = SubmitField('Request Capacity')
