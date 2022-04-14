from flask import render_template, request
from flask_login import current_user

from .models.cart import Cart
from .models.category import Category

from flask import Blueprint

bp = Blueprint('cart', __name__)

@bp.route('/cart', methods=['POST', 'GET'])
