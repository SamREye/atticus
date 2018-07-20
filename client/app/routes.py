from flask import flash, render_template, Response, redirect, url_for
from app import app
from app.forms import LoginForm
from flask_login import login_required, current_user, login_user, logout_user
from app.models import User

@app.route("/")
@app.route("/index")
@login_required
def index():
    return Response("It works!"), 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
