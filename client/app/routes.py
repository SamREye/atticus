from flask import render_template, Response
from app import app
from app.forms import LoginForm

@app.route("/")
@app.route("/index")
def index():
    return Response("It works!"), 200

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)

