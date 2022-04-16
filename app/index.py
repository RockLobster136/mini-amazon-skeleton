from flask import render_template
from flask_login import current_user
import datetime

from .models.product import Product
from .models.purchase import Purchase
from .models.feedback import ProductFeedback
from .models.inventory import Inventory

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    # get all available products for sale:
    products = ProductFeedback.summary_rating(True)
    return render_template('index.html',
                           avail_products=products)
