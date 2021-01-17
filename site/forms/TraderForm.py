from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class TraderForm(FlaskForm):
    product = SelectField(u'Product', validators=[DataRequired()], coerce=str)
    buyupperthreshold = DecimalField(u'BUY Upper Threshold',validators=[NumberRange(min=0,max=100, message='Must be between 0-100')], number_format="#.00")
    buylowerthreshold = DecimalField(u'BUY Lower Threshold',validators=[NumberRange(min=-100,max=0, message='Must be between -100-0')], places=2)
    sellupperthreshold = DecimalField(u'SELL Upper Threshold',validators=[NumberRange(min=0,max=100, message='Must be between 0-100')], places=2)
    selllowerthreshold = DecimalField(u'SELL Lower Threshold',validators=[NumberRange(min=-100,max=0, message='Must be between -100-0')], places=2)
    submit = SubmitField(u'Submit')