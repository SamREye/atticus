from flask import flash, render_template, Response, redirect
from app import app
from app.forms import LoginForm

@app.route("/")
@app.route("/index")
def index():
    return Response("It works!"), 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)
