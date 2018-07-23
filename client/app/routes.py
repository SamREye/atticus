from flask import flash, render_template, Response, redirect, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm, CreateTemplateForm
from flask_login import login_required, current_user, login_user, logout_user
from app.models import User, Template, Contract

@app.route("/")
@app.route("/index")
@app.route("/home")
@login_required
def index():
    templates = db.session.query(Template).filter(Template.owner_id == current_user.id).all()
    contracts = db.session.query(Contract).filter(Contract.owner_id == current_user.id).all()
    return render_template('home.html', title='Home', contracts=contracts, templates=templates)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

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

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@app.route('/template/new', methods=['GET', 'POST'])
@login_required
def create_template():
    form = CreateTemplateForm()
    if form.validate_on_submit():
        template = Template(title=form.title.data, code=form.code.data, body=form.body.data, party_labels=form.party_labels.data, params=form.params.data, owner_id=current_user.id)
        db.session.add(template)
        db.session.commit()
        parties = template.get_party_labels()
        if len(parties) > 0:
            flash('{} Parties have been established'.format(len(parties)))
        else:
            flash('Warning: No parties were established in the template')
        params = template.get_params()
        if len(params) > 0:
            flash('{} Params have been established'.format(len(params)))
        else:
            flash('Warning: No params were established in the template')
        db.session.commit()
        flash('Template saved.')
        return redirect(url_for('user', username=current_user.username))
    return render_template('create_template.html', title='Create a new Template', form=form)

@app.route('/template/list')
@login_required
def list_templates():
    templates = Template.query.all()
    return render_template('list_templates.html', templates=templates)

