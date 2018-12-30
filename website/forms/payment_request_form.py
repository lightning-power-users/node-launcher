from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange


class PaymentRequestForm(FlaskForm):
    value = IntegerField('Value (sats)', validators=[DataRequired(),
                                                     NumberRange(min=100, max=4294967)],
                         default=50000)
    memo = StringField('Memo', validators=[Length(max=1024)],
                       default='Tip')
    generate_invoice = SubmitField('Get PayReq')
