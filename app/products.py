from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,DecimalField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l

from .models.user import User
from .models.purchase import Purchase
from .models.product import Product
from .models.inventory import Inventory
from .models.feedback import ProductFeedback, SellerFeedback

from flask import Blueprint
bp = Blueprint('products', __name__)

class ProductForm(FlaskForm):
    name = StringField(_l('Product Name'), validators=[DataRequired()])
    category = StringField(_l('Product Category'), validators=[DataRequired()])
    description = StringField(_l('Product Description'), validators=[DataRequired()])
    price = FloatField(_l('Product Price'), validators=[InputRequired()])
    image = StringField(_l('Product Image'), validators=[DataRequired()])
    submit = SubmitField(_l('Add Product'))

# unfinished
@bp.route('/createProduct', methods=['GET', 'POST'])
def createProduct():
    form = ProductForm()
    if form.validate_on_submit(): 
            if Product.add_prod(
                form.name.data,
                form.category.data,
                form.description.data,
                form.image.data,
                form.available.data,
                #current_user.id
            ):
                flash('Product added successfully!')       
                return redirect(url_for('index.index'))

    return render_template('createProduct.html', form=form)
    # no createProduct.html yet

