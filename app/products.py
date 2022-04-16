from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l

from .models.user import User
from .models.product import Product

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

class SearchForm_prod(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    sort_by = SelectField('Sort By', choices = ["price","availability"], validators = [DataRequired()])
    firstname = StringField('Seller First Name')
    lastname = StringField('Seller Last Name')
    des = StringField('Product Description')
    cat = SelectField('Filter by Product Category', choices = [])
    price_l = DecimalField('Product Price Lower Bound')
    price_h = DecimalField('Product Price Upper Bound')
    rating_l = DecimalField('Product Rating Lower Bound', validators = [NumberRange(min=1, max=10, message = 'Enter a number between 1 to 10')])
    rating_h = DecimalField('Product Rating Upper Bound', validators = [NumberRange(min=1, max=10, message = 'Enter a number between 1 to 10')])
    avail = DecimalField('Minimum Number of Product Available')
    submit = SubmitField('Search')

@bp.route('/searchProduct', methods=['GET', 'POST'])
def searchProduct():
    form = SearchForm_prod()
    if form.validate_on_submit():
        form.cat.choices = Product.get_prod_cat()
        if Product.search_prod(from.name.data.lower(), form.sort_by.data, form.firstname.data.lower(), form.search_lastname.data.lower(), form.des.data.lower(),
        form.cat.data, form.price_l.data, form.price_h.data, form.rating_l.data, form.rating_h.data, form.avail.data):
            result = Product.search_prod(from.name.data.lower(), form.sort_by.data, form.firstname.data.lower(), form.search_lastname.data.lower(), form.des.data.lower(),
            form.cat.data, form.price_l.data, form.price_h.data, form.rating_l.data, form.rating_h.data, form.avail.data)
            return render_template('find_user_result.html', result = result)
        else:
            flash("We need more information for find the person you want. Please try again.")
            return render_template('find_user.html', form = form)
    else:
        if not form.firstname.data:
            form.search_firstname.data = "optional"
        if not form.lastname.data:
            form.search_lastname.data = "optional"
        if not form.des.data:
            form.des.data = "optional"
        if not form.price_l.data:
            form.price_l.data = 0
        if not form.price_h.data:
            form.price_h.data = 9999999999999999
        if not form.rating_l.data:
            form.rating_l.data = 1
        if not form.rating_h.data:
            form.rating_h.data = 10
        if not form.avail.data:
            form.avail.data = 1
        return render_template('find_user.html', form = form)
