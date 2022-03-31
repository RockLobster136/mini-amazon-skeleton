from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User


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
        return render_template('info.html', accountnum = accountnum, firstname = firstname,
        lastname = lastname, email = email, balance = balance)
    else:
        return redirect(url_for('users.login'))

class EditInfoForm(FlaskForm):
    accountnum = StringField('Account Number')
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
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
        email_temp = current_user.email
        if form.validate_on_submit():
            if current_user.firstname != form.firstname.data:
                firstname_temp = form.firstname.data
            if current_user.lastname != form.lastname.data:
                lastname_temp = form.lastname.data
            if current_user.email != form.email.data:
                if User.email_exists(form.email.data):
                    flash("email already exists")
                    return render_template('editinfo.html', accountnum = id, form = form)
                else:
                    email_temp = form.email.data
            if User.edit(id, email_temp, firstname_temp, lastname_temp):
                return render_template('info.html', accountnum = id, firstname = firstname_temp,
                lastname = lastname_temp, email = email_temp, balance = balance)
            flash("Something is wrong! Please try again!")
        else:
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
                lastname = current_user.lastname, email = current_user.email, balance = new_balance)
            flash("Something is wrong! Please try again!")
        else:
            flash("Enter a negative amount for withdrawal.")
            return render_template('fund.html', accountnum = id, form = form)
    else:
        return redirect(url_for('users.login'))
