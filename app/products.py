# from flask import render_template, redirect, url_for, flash, request
# from werkzeug.urls import url_parse
# from flask_login import login_user, logout_user, current_user
# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, BooleanField, SubmitField
# from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
# from flask_babel import _, lazy_gettext as _l

# from .models.user import User
# from .models.product import Product

# from flask import Blueprint
# bp = Blueprint('products', __name__)

# class ProductForm(FlaskForm):
#     name = StringField(_l('Product Name'), validators=[DataRequired()])
#     category = StringField(_l('Product Category'), validators=[DataRequired()])
#     description = StringField(_l('Product Description'), validators=[DataRequired()])
#     image = StringField(_l('Product Image'), validators=[DataRequired()])
#     submit = SubmitField(_l('Add Product'))

# @bp.route('/ProductPages/<productID>')
# def product_page(productID):
    
#     user_creator = False
#     product = Product.get(productID)
#     #user = User.get(product.creator_id)
#     #sellers = Seller.get_seller_by_pid(productID)
#     #sellerNames = []
#     if current_user.is_authenticated:
#         user_seller = User.is_seller(current_user.id)
#     else:
#         user_seller = False

#     if current_user.is_authenticated:
#         if user.id == current_user.id:
#             user_creator = True

#     # for idx in range(len(sellers)):
#     #     seller = sellers[idx]
#     #     sellerNames.append([0,0])
#     #     sellerNames[idx][0] = User.get(seller.seller_id)
#     #     sellerNames[idx][1] = seller.quantity
#     #     print(sellerNames[idx])

#     #reviews = Product.ratings(product.pid)

#     #num_ratings = len(reviews)
#     #average_rating = sum(int(review[0]) for review in reviews) / (num_ratings if num_ratings else 1)

#     return render_template('productPage.html',
#                             #product=product,
#                             #user=user,
#                             #sellerNames=sellerNames,
#                             #reviews=reviews,
#                             #num_ratings=num_ratings,
#                             #average_rating=average_rating,
#                             #user_seller=user_seller,
#                             #user_creator=user_creator)


# @bp.route('/createProduct', methods=['GET', 'POST'])
# def createProduct():
#     form = ProductForm()
#     if form.validate_on_submit(): 
#             if Product.add_prod(
#                 form.name.data,
#                 form.category.data,
#                 form.description.data,
#                 form.image.data,
#                 form.available.data,
#                 #current_user.id
#             ):
#                 flash('Product added successfully!')       
#                 return redirect(url_for('index.index')) ####### check if the parameter is correct

#     return render_template('createProduct.html', form=form)