from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class ChannelRequestForm(FlaskForm):
    pub_key = StringField('Your PubKey', validators=[DataRequired()])
    twitter_username = StringField('Twitter Username (optional)')
    email_address = StringField('E-mail Address (optional)')
    fee_rate = SelectField('Fee Rate')
    channel_size = SelectField('Channel Size')
    request_channel = SubmitField('Request Channel')
