from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, NumberRange

class TraderForm(FlaskForm):
    title = "Add Trader"
    availablefunds = 0
    traderid = HiddenField(u'TraderId')
    product = HiddenField(u'Product', validators=[DataRequired()])
    loglevel = SelectField(u'Log Level', validators=[DataRequired()], coerce=int)
    maxpurchaseamount = DecimalField(u'MAX purchase amount',validators=[NumberRange(min=0, message='Must be greater than 0')], number_format="#.00")
    buyupperthreshold = DecimalField(u'BUY Upper Threshold',validators=[NumberRange(min=0,max=100, message='Must be between 0-100')], number_format="#.00")
    buylowerthreshold = DecimalField(u'BUY Lower Threshold',validators=[NumberRange(min=-100,max=0, message='Must be between -100-0')], places=2)
    sellupperthreshold = DecimalField(u'SELL Upper Threshold',validators=[NumberRange(min=0,max=100, message='Must be between 0-100')], places=2)
    selllowerthreshold = DecimalField(u'SELL Lower Threshold',validators=[NumberRange(min=-100,max=0, message='Must be between -100-0')], places=2)
    submit = SubmitField(u'Submit')