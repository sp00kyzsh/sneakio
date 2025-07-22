from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, SelectField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from datetime import date

class SneakerForm(FlaskForm):
    sku = StringField('SKU', validators=[Optional(), Length(max=50)])
    brand = StringField('Brand', validators=[DataRequired(), Length(min=1, max=50)])
    model = StringField('Model', validators=[DataRequired(), Length(min=1, max=100)])
    size = StringField('Size', validators=[DataRequired(), Length(min=1, max=10)])
    category = SelectField('Category', 
                          choices=[("Men's", "Men's"), ("Women's", "Women's"), ("Children's", "Children's")],
                          validators=[DataRequired()], default="Men's")
    colorway = StringField('Colorway', validators=[DataRequired(), Length(min=1, max=100)])
    retail_price = DecimalField('Retail Price', validators=[Optional(), NumberRange(min=0)])
    release_date = DateField('Release Date', validators=[Optional()])
    purchase_price = DecimalField('Purchase Price', validators=[DataRequired(), NumberRange(min=0)])
    purchase_date = DateField('Purchase Date', validators=[DataRequired()], default=date.today)
    condition = SelectField('Condition', 
                          choices=[('New', 'New'), ('Used', 'Used'), ('Deadstock', 'Deadstock')],
                          validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    listing_price = DecimalField('Listing Price', validators=[Optional(), NumberRange(min=0)])

class SaleForm(FlaskForm):
    sneaker_id = SelectField('Sneaker', coerce=int, validators=[DataRequired()])
    sale_price = DecimalField('Sale Price', validators=[DataRequired(), NumberRange(min=0)])
    sale_date = DateField('Sale Date', validators=[DataRequired()], default=date.today)
    buyer_info = StringField('Buyer Info', validators=[Optional(), Length(max=200)])
    platform = SelectField('Platform', 
                          choices=[('StockX', 'StockX'), ('GOAT', 'GOAT'), ('eBay', 'eBay'), 
                                 ('Facebook', 'Facebook'), ('Instagram', 'Instagram'), 
                                 ('Local', 'Local'), ('Other', 'Other')],
                          validators=[Optional()])
    tracking_number = StringField('Tracking Number', validators=[Optional(), Length(max=50)])
    fees = DecimalField('Fees', validators=[Optional(), NumberRange(min=0)], default=0.0)
    shipping_cost = DecimalField('Shipping Cost', validators=[Optional(), NumberRange(min=0)], default=0.0)

class ListingForm(FlaskForm):
    platform = SelectField('Platform', 
                          choices=[('StockX', 'StockX'), ('GOAT', 'GOAT'), ('eBay', 'eBay'), 
                                 ('Facebook', 'Facebook Marketplace'), ('Instagram', 'Instagram'), 
                                 ('Local', 'Local Sale'), ('Grailed', 'Grailed'), ('Vinted', 'Vinted'), 
                                 ('Depop', 'Depop'), ('Other', 'Other')],
                          validators=[DataRequired()])
    listing_url = StringField('Listing URL', validators=[Optional(), Length(max=500)])
    listing_price = DecimalField('Listing Price', validators=[DataRequired(), NumberRange(min=0)])
    listing_status = SelectField('Status', 
                               choices=[('Active', 'Active'), ('Paused', 'Paused'), ('Sold', 'Sold'), ('Expired', 'Expired')],
                               validators=[DataRequired()], default='Active')
    date_listed = DateField('Date Listed', validators=[DataRequired()], default=date.today)
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
