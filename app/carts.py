from flask import render_template, request
from flask_login import login_user, logout_user, current_user
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
import datetime
from flask_login import login_user, logout_user, current_user
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField,IntegerField,SelectField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo,NumberRange
from .models.user import User
from .models.purchase import Purchase
from .models.product import Product
from .models.inventory import Inventory
from .models.feedback import ProductFeedback, SellerFeedback
from .models.cart import Cart
from .models.category import Category
from .models.product import Product

from flask import Blueprint

bp = Blueprint('cart', __name__)

@bp.route('/cart', methods=['POST', 'GET'])
def cart():
    # error messages
    checkout_now = False
    checkout_error = False

    if request.method == 'POST' and current_user.is_authenticated:
        if request.form['action'] == 'add':
            inventory_id = request.form['inventory_id']
            product_id = request.form['product_id']
            quantity = request.form['quantity']
            Cart.add_to_cart(current_user.id, inventory_id, quantity, product_id)
        if request.form['action'] == 'remove':
            inventory_id = request.form['inventory_id']
            Cart.remove_from_cart(current_user.id, inventory_id)
        if request.form['action'] == 'change_quantity':
            new_quantity = request.form['quantity']
            if int(new_quantity) >= 1:
                Cart.change_quantity(current_user.id, request.form['inventory_id'], new_quantity)
        if request.form['action'] == 'checkout':
            try:
                Cart.palce_order(current_user.id)
                checkout_now = True
            except Exception as e:
                checkout_error = True

    this_cart = []
    if current_user.is_authenticated:
        # current login user
        this_cart = Cart.user_cart(current_user.id)
    else:
        pass
    categories = Product.get_prod_cat()
    total_price = sum([prod.product_price * prod.quantity for prod in this_cart]) if len(this_cart) > 0 else 0
    # render the page by adding information to the index.html file
    return render_template('cart.html',
                           cart=this_cart,
                           categories=categories,
                           checkout_now=checkout_now,
                           total_price=total_price,
                           checkout_error=checkout_error)