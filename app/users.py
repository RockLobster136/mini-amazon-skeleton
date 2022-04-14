
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
from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    becomeSeller = BooleanField('I am a seller')
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         form.becomeSeller.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

@bp.route('/info', methods=['GET','POST'])
def info():
    if current_user.is_authenticated:
        accountnum = current_user.id
        firstname = current_user.firstname
        lastname = current_user.lastname
        email = current_user.email
        balance = current_user.balance
        address = current_user.address
        isSeller = current_user.isSeller
        return render_template('info.html', accountnum = accountnum, firstname = firstname,
        lastname = lastname, email = email, balance = balance, address = address, isSeller = isSeller)
    else:
        return redirect(url_for('users.login'))

class EditInfoForm(FlaskForm):
    accountnum = StringField('Account Number')
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Commit Changes')


@bp.route('/info/edit', methods=['GET','POST'])
def edit_info():
    if current_user.is_authenticated:
        form = EditInfoForm()
        id = current_user.id
        balance = current_user.balance
        form.accountnum.data = id
        firstname_temp = current_user.firstname
        lastname_temp = current_user.lastname
        address_temp = current_user.address
        email_temp = current_user.email
        if form.validate_on_submit():
            if current_user.email != form.email.data:
                if User.email_exists(form.email.data):
                    flash("email already exists")
                    return render_template('editinfo.html', accountnum = id, form = form)
                else:
                    email_temp = form.email.data
            if User.edit(id, email_temp, firstname_temp, lastname_temp, address_temp):
                return render_template('info.html', accountnum = id, firstname = firstname_temp,
                lastname = lastname_temp, email = email_temp, balance = balance, address = address_temp)
            flash("Something is wrong! Please try again!")
        else:
            if not form.firstname.data:
                form.firstname.data = current_user.firstname
            if not form.lastname.data:
                form.lastname.data = current_user.lastname
            if not form.address.data:
                form.address.data = current_user.address
            if not form.email.data:
                form.email.data = current_user.email
            return render_template('editinfo.html', accountnum = id, form = form)
    else:
        return redirect(url_for('users.login'))

class ChangePasswordForm(FlaskForm):
    accountnum = StringField('Account Number')
    password = PasswordField('New Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Commit Changes')

@bp.route('/info/password', methods=['GET','POST'])
def change_password():
    if current_user.is_authenticated:
        form = ChangePasswordForm()
        id = current_user.id
        form.accountnum.data = id
        if form.validate_on_submit():
            if User.change_password(id,form.password.data):
                logout_user()
                flash("Password Updated")
                return redirect(url_for('users.login'))
            flash("Something is wrong! Please try again!")
        else:
            return render_template('password.html', accountnum = id, form = form)
    else:
        return redirect(url_for('users.login'))

class FundForm(FlaskForm):
    accountnum = StringField('Account Number')
    amount = DecimalField('Amount', validators=[DataRequired()])
    submit = SubmitField('Commit')

@bp.route('/info/fund', methods=['GET','POST'])
def fund():
    if current_user.is_authenticated:
        form = FundForm()
        id = current_user.id
        form.accountnum.data = id
        if form.validate_on_submit():
            if (len(str(abs(form.amount.data))) - len(str(abs(int(form.amount.data))))) > 3:
                flash("Please round your input to 2 decimal places.")
                return render_template('fund.html', accountnum = id, form = form)
            new_balance = current_user.balance + form.amount.data
            if new_balance < 0:
                flash("Insufficient Fund.")
                return render_template('fund.html', accountnum = id, form = form)
            if User.mgmt_fund(id,new_balance):
                return render_template('info.html', accountnum = id, firstname = current_user.firstname,
                lastname = current_user.lastname, email = current_user.email, balance = new_balance, address = current_user.address)
            flash("Something is wrong! Please try again!")
        else:
            flash("Enter a negative amount for withdrawal.")
            return render_template('fund.html', accountnum = id, form = form)
    else:
        return redirect(url_for('users.login'))

@bp.route('/history', methods=['GET','POST'])
def history():
    if current_user.is_authenticated:
        if current_user.isSeller:
            record = Inventory.get_all_by_uid_since(
                current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
            
        else:
            record = User.get_pur(current_user.id)
    else:
        record = None
    return render_template('history.html',
                           purchase_history=record)


class InventoryForm(FlaskForm):
    prodName = SelectField('Product Name',choices=[])
    prodCat = SelectField('Product Category',choices=[])
    Price = DecimalField('Price', 
            validators=[DataRequired(), NumberRange(min=0, message='Can not enter negative number')])
    Quantity = IntegerField('Quantity', 
                validators=[DataRequired(),NumberRange(min=0, message='Can not enter negative number')])
    delete =SelectField('Delete this Inventory', choices = ["No","Yes"], validators = [DataRequired()])
    submit = SubmitField('Commit')

class SearchForm_hist(FlaskForm):
    search_name = StringField('Product Name', validators=[DataRequired()])
    sort_by = SelectField("Sort by", choices = ["Product Name","Date","Seller","Category"])
    value_l = DecimalField('Value Lower Bound')
    value_h = DecimalField('Value Upper Bound')
    date_l = DateField('Date Earliest', format='%m/%d/%Y')
    date_h = DateField('Date Latest', format='%m/%d/%Y')    
    submit = SubmitField('Search')

@bp.route("/history/search", methods=['GET','POST'])
def search():
    form = SearchForm_hist()
    if form.validate_on_submit():
        if form.sort_by.data == "Product Name":
            form.sort_by.data = 'Pro.name'
        if form.sort_by.data == "Date":
            form.sort_by.data = 'Pur.time_purchased'
        if form.sort_by.data == "Seller":
            form.sort_by.data = 'Pur.sid'
        if form.sort_by.data == "Category":
            form.sort_by.data = 'Pro.category'
        if User.search_pur(current_user.id, form.search_name.data, form.sort_by.data, form.value_l.data, form.value_h.data, form.date_l.data, form.date_h.data ):
            result = User.search_pur(current_user.id, form.search_name.data, form.sort_by.data, form.value_l.data, form.value_h.data, form.date_l.data, form.date_h.data )
            return render_template('search_result.html', result = result,order_search = False)
            flash("111")
        else:
            flash("Invalid search. Please try again.")
            return render_template('search.html', form = form,order_search = False)
    else:
        if not form.value_l.data:
            form.value_l.data = 0
        if not form.value_h.data:
            form.value_h.data = 9999999999999999
        if not form.date_l.data:
            form.date_l.data = datetime.datetime(1980, 9, 14, 0, 0, 0)
        if not form.date_h.data:
            form.date_h.data = datetime.datetime.now()
        return render_template('search.html', form = form,order_search = False)

class SearchForm_user(FlaskForm):
    search_firstname = StringField('User First Name')
    search_lastname = StringField('User Last Name')
    search_role = SelectField('User Role', choices = ["Buyer","Seller","All"])
    submit = SubmitField('Search')

@bp.route("/finduser", methods=['GET','POST'])
def search_user():
    form = SearchForm_user()
    if form.validate_on_submit():
        if User.search_user(form.search_firstname.data.lower(), form.search_lastname.data.lower(), form.search_role.data):
            result = User.search_user(form.search_firstname.data.lower(), form.search_lastname.data.lower(), form.search_role.data)
            return render_template('find_user_result.html', result = result)
        else:
            flash("We need more information for find the person you want. Please try again.")
            return render_template('find_user.html', form = form)
    else:
        if not form.search_firstname.data:
            form.search_firstname.data = "optional"
        if not form.search_lastname.data:
            form.search_lastname.data = "optional"
        return render_template('find_user.html', form = form)

@bp.route('/finduser/find_user_result/view_seller/<uid>', methods=['GET','POST'])
def view_seller(uid = None):
    if uid:
        seller_info = User.get_seller(uid)
        feedback = User.get_seller_feedback(uid)
        return render_template("view_seller.html", seller_info = seller_info, feedback = feedback)
    return None

@bp.route('/history/addinventory', methods=['GET','POST'])
def addinventory():
    if current_user.is_authenticated and current_user.isSeller:
        form = InventoryForm()
        if form.validate_on_submit:
            
            form.prodCat.choices = Product.get_prod_cat()
            if Product.get_by_category(form.prodCat.data):
                form.prodName.choices = [product for product in Product.get_by_category(form.prodCat.data)]
            sellerId = current_user.id
            pid = Product.prod_find(form.prodName.data)
            if form.Quantity.data:
                if Inventory.add_inventory(sellerId,pid,form.Quantity.data,form.Price.data):
                        flash("Successfully created new Inventory")
                        return render_template('addinventory.html',form = form)
                else:
                    flash("Error: no inventory update. Your probably have created this inventory already.")
        return render_template('addinventory.html',form = form)
    else:
        return redirect(url_for('users.login'))

@bp.route("/history/update/<iid>",methods=['GET','POST'])
def update_inventory(iid = None):
    form = InventoryForm()
    if form.validate_on_submit:
        if iid:
            if form.Delete.data == "Yes":
                if Inventory.delete_inventory(iid):
                    flash("Successfully delete this Inventory")
                    return render_template("update.html",form = form)
            elif form.Price.data and form.Quantity.data:
                if Inventory.update_inventory(iid,form.Price.data,form.Quantity.data):
                    flash("Successfully update this Inventory")
                    return render_template("update.html",form = form)
    return render_template("update.html",form = form)


@bp.route('/info/orders', methods=['GET','POST'])
def orders():
    if current_user.is_authenticated:
        if current_user.isSeller:
            record = Purchase.get_seller_orders(
                current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
            for r in record:
                if Purchase.check_order_fulfill(r.order_id,current_user.id):
                    r.batch_status = True
        else:
            record = Purchase.get_all_by_uid_since(
                current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        record = None
    return render_template('orders.html',
                           purchase_history=record)

class OrderForm(FlaskForm):
    cancelOrder = SelectField("Cancel this Order", choices = ["No","Yes"])
    fulfillOrder = SelectField("Fulfill this Order", choices = ["No","Yes"])
    submit = SubmitField('Commit')

@bp.route('/orders/manage/<oid>', methods=['GET','POST'])
def manage_orders(oid = None):
    form = OrderForm()
    if form.validate_on_submit():
        if oid: 
            if form.fulfillOrder.data == "Yes":
                time = datetime.datetime.now()
                if Purchase.fulfill_item(oid,time):
                    flash("Successfully Fulfill")
            elif form.cancelOrder.data == "Yes":
                if Purchase.delete_item(oid):
                    flash("Successfully delete")
            return render_template("manageorders.html",form = form)
    return render_template("manageorders.html",form = form)

@bp.route('/orders/view/<oid>', methods=['GET','POST'])
def view_order(oid = None):
    if oid:
        print(oid)
        order_detail = Purchase.get_seller_order_view(oid)
        seller_info = Purchase.get_seller_info(oid)
        return render_template("view.html",order_detail = order_detail,seller_info = seller_info)
    return render_template("view.html",order_detail = None,seller_info =None)


class SearchForm(FlaskForm):
    fulfill_status = SelectField("Fulfillment Status", choice = ["Fulfilled", "Not Fulfilled"])
    prodName = StringField("Product Name")
    year_range = SelectField("Recent", choices = ["1 month","3 months", "1 years","All"])

@bp.route('/orders/search', methods=['GET','POST'])
def search_order():
    form = SearchForm()
    if form.year_range.data == "1 month":
        date = datetime.datetime



class SearchForm_order(FlaskForm):
    search_name = StringField('Product Name', validators=[DataRequired()])
    sort_by = SelectField("Show", choices = ["All Orders","Unfilfilled Orders","Fulfilled Orders"])
    value_l = DecimalField('Value Lower Bound')
    value_h = DecimalField('Value Upper Bound')
    date_l = DateField('Date Earliest', format='%m/%d/%Y')
    date_h = DateField('Date Latest', format='%m/%d/%Y')    
    submit = SubmitField('Search')

@bp.route("/orders/order_search", methods=['GET','POST'])
def order_search():
    form = SearchForm_order()
    if form.validate_on_submit():
        if Purchase.search_order(current_user.id, form.search_name.data, form.sort_by.data, form.value_l.data, form.value_h.data, form.date_l.data, form.date_h.data ):
            result = Purchase.search_order(current_user.id, form.search_name.data, form.sort_by.data, form.value_l.data, form.value_h.data, form.date_l.data, form.date_h.data )
            return render_template('search_result.html', result = result,order_search = True)
        else:
            flash("Invalid search. Please try again.")
            
            return render_template('search.html', form = form,order_search = True)
    else:
        if not form.value_l.data:
            form.value_l.data = 0
        if not form.value_h.data:
            form.value_h.data = 9999999999999999
        if not form.date_l.data:
            form.date_l.data = datetime.datetime(1980, 9, 14, 0, 0, 0)
        if not form.date_h.data:
            form.date_h.data = datetime.datetime.now()
        return render_template('search.html', form = form,order_search = True)


class low_form(FlaskForm):
    number_threshold = SelectField("Number of Products displayed", choices = [1,3,5,10],validators=[DataRequired()])
    quantity_threshold = SelectField('Product Less Than', choices = [1,5,10,20,100],validators=[DataRequired()])
    submit = SubmitField('commit')
class prod(FlaskForm):
    prdoname = SelectField("Select Product", choices = [],validators=[DataRequired()])
    submit = SubmitField('Select')

@bp.route("/insights", methods=['GET','POST'])
def seller_insight():
    form = prod()
    prods = Purchase.get_seller_orders(
                current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    prodnames = [p.prodname for p in prods]
    form.prdoname.choices = prodnames
    if form.validate_on_submit():
        name = form.prdoname.data.replace(" ", "-")
        return render_template('insights.html',form = form,name = name)
    return render_template('insights.html',form = form)

@bp.route("/insights/<prodname>", methods=['GET','POST'])
def prod_viz(prodname = None):
    sid = current_user.id  
    if prodname:
        prodname = prodname.replace("-"," ")
        prod_data = Purchase.prod_trend(sid,prodname)
        return render_template("viz.html",prod_data = prod_data)
    

@bp.route("/insights/low-inventory", methods=['GET','POST'])
def low_inventory():
    form = low_form()
    if form.validate_on_submit():
        if Inventory.get_least_n(current_user.id,form.number_threshold.data,form.quantity_threshold.data):
            record = Inventory.get_least_n(current_user.id,form.number_threshold.data,form.quantity_threshold.data)
            return render_template("lowInventory_result.html",record = record)
        else:
            flash("No Result")
    return render_template("lowInventory.html",form = form)
    





# Feedback

class FeedbackForm(FlaskForm):
    prodName = SelectField('Product Name', choices = [])
    sellerName = SelectField('Seller Name', choices = [])
    rating = SelectField('Rating', choices = [i for i in range(0,11)])
    review = StringField('Review')
    delete = SelectField('Delete this review?', choices = ['No','Yes'])
    submit = SubmitField('Commit')


@bp.route('/feedback', methods=['GET','POST'])
def feedback():
    # retrive buyer's feedbacks
    if current_user.is_authenticated:
        product_feedbacks = ProductFeedback.get_all_feedbacks(current_user.id)
        seller_feedbacks = SellerFeedback.get_all_feedbacks(current_user.id)
        return render_template('feedback.html', product_feedbacks = product_feedbacks, seller_feedbacks = seller_feedbacks)
    else:
        return render_template('feedback.html', product_feedbacks = None, seller_feedbacks = None)

@bp.route('/feedback/add_feedback/<isseller>', methods=['GET','POST'])
def add_feedback(isseller =None):
    # retrive buyer's feedbacks
    if current_user.is_authenticated:
        form = FeedbackForm()
        if isseller == "Yes":
            sids = SellerFeedback.non_reviewed_sellers(current_user.id)
            choices = [User.get_user_name(sid)[0] for sid in sids]
            form.sellerName.choices = choices
            print(choices)
            if form.rating.data:
                sid = sids[choices==form.sellerName.data]
                if SellerFeedback.add_feedback(current_user.id, sid, form.rating.data, form.review.data):
                    flash("Succesfully added review!")
                    return render_template('add_feedback.html', form=form,isseller = isseller)
        else:
            choices = ProductFeedback.non_reviewed_products(current_user.id)
            form.prodName.choices = choices
            if form.rating.data:
                pid = Product.prod_find(form.prodName.data)
                if ProductFeedback.add_feedback(current_user.id, pid, form.rating.data, form.review.data):
                    flash("Succesfully added review!")
        return render_template('add_feedback.html', form=form,isseller = isseller)
    else:
        return render_template('add_feedback.html', form=None,isseller = None)

@bp.route('/feedback/edit_feedback/<feedback_id>-<isseller>', methods=['GET','POST'])
def edit_feedback(feedback_id = None, isseller = None):
    if feedback_id:
        form = FeedbackForm()
        if form.rating.data or form.review.data or form.delete.data:
            if isseller == "No":
                if ProductFeedback.update_product_review(feedback_id, form.rating.data, form.review.data, form.delete.data == 'Yes'):
                    if form.delete.data == "Yes":
                        flash("Successfully deleted review")
                    else:
                        flash("Successfully edited review")
                    return render_template('edit_feedback.html', form = form)
            else:
                if SellerFeedback.update_seller_review(feedback_id, form.rating.data, form.review.data, form.delete.data == 'Yes'):
                    if form.delete.data == "Yes":
                        flash("Successfully deleted review")
                    else:
                        flash("Successfully edited review")
                    return render_template('edit_feedback.html', form = form)
        return render_template('edit_feedback.html', form = form)


