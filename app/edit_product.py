from flask import render_template, request
from flask_login import current_user

from .models.product import Product
from .models.category import Category
from .models.inventory import Inventory

from flask import Blueprint, redirect, url_for

bp = Blueprint('edit_product', __name__)

@bp.route('/edit_product', methods=['POST', 'GET'])
@bp.route('/edit_product/<pid>', methods=['GET'])
def edit_product(pid=None):
    if request.method == 'POST':
        if request.form['jump'] == "inventory":
            jump_to_inventory = True
        # if 'image' in request.files:
        #     image_file = request.files['image']
        #     image_path = image_file.filename
        #     if image_path is None or image_path == '' or image_path == '/':
        #         image_path = None
        #     else:
        #         image_file.save(os.path.join(basedir, 'static', image_path))
        # else:
            image_path = None
        if request.form['action'] == 'add':
            new_id = Product.add(request.form['pname'],
                                 current_user.id,
                                 int(request.form['category']),
                                 request.form['description'],
                                 image_path)
            return redirect(f"{url_for('product.product')}/{new_id}", code=302)
        elif request.form['action'] == 'update':
            pid = int(request.form['pid'])
            Product.update(pid,
                           request.form['pname'],
                           current_user.id,
                           int(request.form['category']),
                           request.form['description'],
                           image_path)
            return redirect(f"{url_for('product.product')}/{pid}", code=302)

    dummy_product = Product(...)
    page_title = 'Add New Product'
    action = 'add'
    if pid is not None:
        dummy_product = Product.get(pid)
        page_title = f'Edit Product Information for {dummy_product.name}'
        action = 'update'
    # get all categories
    categories = Product.get_prod_cat()

    return render_template('editProduct.html',
                           dummy_product=dummy_product,
                           categories=categories,
                           page_title=page_title,
                           action=action,
                           jump_to_inventory=jump_to_inventory)
