from flask_mail import Message
from flask import flash, render_template, Response, redirect, url_for
from app import app, db, mail
from app.forms import LoginForm, RegistrationForm, CreateTemplateForm, CreateProposalForm, CloneProposalForm
from flask_login import login_required, current_user, login_user, logout_user
from app.models import User, Template, Contract, Party
import json
from datetime import datetime

contract_actions = {'propose': 'proposed', 'decline': 'declined', 'reconsider': 'proposed', 'sign': 'signed'}
contract_transitions = {
    'draft': {'owner': ['propose', 'clone', 'archive']},
    'proposed': {'cparty': ['sign', 'decline', 'counter'], 'owner': ['withdraw']},
    'declined': {'cparty': ['reconsider', 'archive'], 'owner': ['archive']},
    'partially signed': {'cparty': ['withdraw'], 'owner': ['sign', 'withdraw']},
    'signed': {},
    'archived': {}
}

@app.route("/")
@app.route("/index")
@app.route("/home")
@login_required
def index():
    templates = db.session.query(Template).filter(Template.owner_id == current_user.id).all()
    contracts = db.session.query(Contract).join(Party).filter(Party.user_id == current_user.id).filter(Contract.status == "signed").all()
    proposals = db.session.query(Contract).join(Party).filter(Party.user_id == current_user.id).filter(~Contract.status.in_(["signed", "draft", "archived"])).all()
    drafts = db.session.query(Contract).filter(Contract.status == "draft", Contract.owner_id == current_user.id).all()
    return render_template('home.html', title='Home', proposals=proposals, contracts=contracts, templates=templates, drafts=drafts, transitions=contract_transitions)

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

@app.route('/contacts')
@login_required
def get_contacts():
    users = User.query.all()
    return json.dumps([(u.id, u.username) for u in users])

@app.route('/template/new', methods=['GET', 'POST'])
@login_required
def create_template():
    form = CreateTemplateForm()
    if form.validate_on_submit():
        template = Template(title=form.title.data, code=form.code.data, body=form.body.data, party_labels=form.party_labels.data, params=form.params.data, owner_id=current_user.id)
        db.session.add(template)
        db.session.flush()
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
        return redirect(url_for('index'))
    return render_template('create_template.html', title='Create a new Template', form=form)

@app.route('/template/list')
@login_required
def list_templates():
    templates = Template.query.all()
    return render_template('list_templates.html', templates=templates)

@app.route('/template/<template_id>/party_labels')
def get_template_party_labels(template_id):
    template = Template.query.filter_by(id=template_id).first_or_404()
    return template.party_labels

@app.route('/template/<template_id>/params')
def get_template_params(template_id):
    template = Template.query.filter_by(id=template_id).first_or_404()
    return template.params

@app.route('/contract/<contract_id>/params')
def get_contract_params(contract_id):
    contract = Contract.query.filter_by(id=contract_id).first_or_404()
    return contract.params

@app.route('/template/<template_id>')
def show_template(template_id):
    template = Template.query.filter_by(id=template_id).first_or_404()
    return render_template('template.html', template=template, owner=User.query.get(template.owner_id))

@app.route('/template/<template_id>/raw')
def show_template_raw(template_id):
    template = Template.query.filter_by(id=template_id).first_or_404()
    return json.dumps({'text': template.body, 'code': template.code})

@app.route('/contract/new', methods=['GET', 'POST'])
@login_required
def create_draft():
    form = CreateProposalForm()
    form.template_id.choices = [(t.id, t.title) for t in Template.query.order_by('title')]
    if form.validate_on_submit():
        proposal = Contract(template_id=form.template_id.data, params=form.params.data, status="draft", owner_id=current_user.id)
        db.session.add(proposal)
        db.session.flush()
        for p in json.loads(form.parties.data):
            party = Party(contract_id=proposal.id, role=p['label'], user_id=p['user_id'])
            db.session.add(party)
        db.session.commit()
        flash('Draft saved.')
        return redirect(url_for('index'))
    contacts = User.query.all()
    return render_template('create_draft.html', title='Create a new Draft Proposal', form=form, contacts=contacts)

@app.route('/contract/<contract_id>/clone', methods=['GET', 'POST'])
@login_required
def clone_draft(contract_id):
    contract = db.session.query(Contract).join(Template).filter(Contract.id == contract_id).first()
    role = 'owner' if contract.owner_id == current_user.id else 'cparty'
    if 'clone' not in contract_transitions[contract.status][role]:
        flash('This action is not permitted')
        return redirect(url_for('index'))
    form = CloneProposalForm()
    form.template_id.choices = [(t.id, t.title) for t in Template.query.order_by('title')]
    if form.validate_on_submit():
        proposal = Contract(template_id=form.template_id.data, params=form.params.data, status="draft", owner_id=current_user.id, parent_id=(contract.parent_id or contract.id))
        db.session.add(proposal)
        db.session.flush()
        for p in contract.party:
            party = Party(contract_id=proposal.id, role=p.role, user_id=p.user_id)
            db.session.add(party)
        db.session.commit()
        flash('Draft cloned.')
        return redirect(url_for('index'))
    form.template_id.data = contract.template_id
    form.params.data = contract.params
    return render_template('clone_draft.html', title='Clone a Draft Proposal', form=form, contract_id=contract_id, parties=contract.party)

@app.route('/contract/<contract_id>')
@login_required
def show_draft(contract_id):
    contract = db.session.query(Contract).join(Template).filter(Contract.id == contract_id).first_or_404()
    parties = db.session.query(Party).join(Contract).filter(Contract.id == contract_id).all()
    parent = None
    if contract.parent_id is not None:
        parent = db.session.query(Contract).join(Template).filter(Contract.id == contract.parent_id).first()
    return render_template('contract.html', contract=contract, parties=parties, transitions=contract_transitions, parent=parent)

@app.route('/contract/<contract_id>/archive')
@login_required
def archive_draft(contract_id):
    contract = Contract.query.filter(Contract.id == contract_id).first_or_404()
    role = 'owner' if contract.owner_id == current_user.id else 'cparty'
    if 'propose' not in contract_transitions[contract.status][role]:
        flash('This action is not permitted')
        return redirect(url_for('index'))
    contract.status = "archived"
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/contract/<contract_id>/propose')
@login_required
def propose(contract_id):
    contract = Contract.query.filter(Contract.id == contract_id).first_or_404()
    role = 'owner' if contract.owner_id == current_user.id else 'cparty'
    if 'propose' not in contract_transitions[contract.status][role]:
        flash('This action is not permitted')
        return redirect(url_for('index'))
    contract.status = "proposed"
    db.session.commit()
    msg = Message(subject='Someone sent you a proposal', sender='info@atticus.one', recipients=[p.user.email for p in contract.party if p.user_id != current_user.id], html='<h1>New Proposal</h1><p>Please click <a href="' + url_for('show_draft', contract_id=contract_id, _external=True) + '">here</a> to view the proposal.</p>')
    mail.send(msg)
    return redirect(url_for('index'))

@app.route('/contract/<contract_id>/withdraw')
@login_required
def withdraw(contract_id):
    contract = Contract.query.filter(Contract.id == contract_id).first_or_404()
    role = 'owner' if contract.owner_id == current_user.id else 'cparty'
    if 'withdraw' not in contract_transitions[contract.status][role]:
        flash('This action is not permitted')
        return redirect(url_for('index'))
    contract.status = "draft"
    db.session.commit()
    msg = Message(subject='A proposal of yours has been withdrawn', sender='info@atticus.one', recipients=[p.user.email for p in contract.party if p.user_id != current_user.id], html='<h1>Proposal Withdrawn</h1><p>Please click <a href="' + url_for('show_draft', contract_id=contract_id, _external=True) + '">here</a> to view the proposal.</p>')
    mail.send(msg)
    return redirect(url_for('index'))

@app.route('/contract/<contract_id>/counter')
@login_required
def counter_contract(contract_id):
    contract = Contract.query.filter(Contract.id == contract_id).first_or_404()
    role = 'owner' if contract.owner_id == current_user.id else 'cparty'
    if 'counter' not in contract_transitions[contract.status][role]:
        flash('This action is not permitted')
        return redirect(url_for('index'))
    clone = Contract(template_id=contract.template_id, params=contract.params, status="draft", owner_id=current_user.id)
    db.session.add(clone)
    db.session.commit()
    flash('Counter Proposal created')
    msg = Message(subject='Someone countered a proposal', sender='info@atticus.one', recipients=[p.user.email for p in contract.party if p.user_id != current_user.id], html='<h1>New Counter Proposal</h1><p>Please click <a href="' + url_for('show_draft', contract_id=clone.id, _external=True) + '">here</a> to view the proposal.</p>')
    mail.send(msg)
    return redirect(url_for('index'))

@app.route('/contract/<contract_id>/reconsider')
@login_required
def reconsider_contract(contract_id):
    contract = Contract.query.filter(Contract.id == contract_id).first_or_404()
    role = 'owner' if contract.owner_id == current_user.id else 'cparty'
    if 'reconsider' not in contract_transitions[contract.status][role]:
        flash('This action is not permitted')
        return redirect(url_for('index'))
    contract.status = "proposed"
    db.session.commit()
    flash('Proposal reconsidered')
    #msg = Message(subject='Someone is reconsidering a proposal', sender='info@atticus.one', recipients=[p.user.email for p in contract.party if p.user_id != current_user.id], html='<h1>Proposal Reconsidered</h1><p>Please click <a href="' + url_for('show_draft', contract_id=contract_id, _external=True) + '">here</a> to view the proposal.</p>')
    #mail.send(msg)
    return redirect(url_for('index'))

@app.route('/contract/<contract_id>/decline')
@login_required
def decline_proposal(contract_id):
    contract = Contract.query.filter(Contract.id == contract_id).first_or_404()
    role = 'owner' if contract.owner_id == current_user.id else 'cparty'
    if 'decline' not in contract_transitions[contract.status][role]:
        flash('This action is not permitted')
        return redirect(url_for('index'))
    contract.status = "declined"
    db.session.commit()
    flash('Proposal declined')
    msg = Message(subject='Someone declined a proposal', sender='info@atticus.one', recipients=[p.user.email for p in contract.party if p.user_id != current_user.id], html='<h1>Proposal Declined</h1><p>Please click <a href="' + url_for('show_draft', contract_id=contract_id, _external=True) + '">here</a> to view the proposal.</p>')
    mail.send(msg)
    return redirect(url_for('index'))

@app.route('/contract/<contract_id>/sign')
@login_required
def sign_contract(contract_id):
    contract = Contract.query.filter(Contract.id == contract_id).first_or_404()
    role = 'owner' if contract.owner_id == current_user.id else 'cparty'
    if 'sign' not in contract_transitions[contract.status][role]:
        flash('This action is not permitted')
        return redirect(url_for('index'))
    all_signed = True
    for party in contract.party:
        if party.user_id == current_user.id:
            if party.signed_on is None:
                party.signed_on = datetime.now()
            else:
                flash('Contract is already signed by this party')
        else:
            if party.signed_on is None:
                all_signed = False
    if all_signed:
        contract.status = "signed"
        db.session.commit()
        flash('Contract signed--now in effect!')
    else:
        contract.status = "partially signed"
        db.session.commit()
        flash('Contract signed--now pending other signature(s)')
    msg = Message(subject='Someone signed a contract', sender='info@atticus.one', recipients=[p.user.email for p in contract.party if p.user_id != current_user.id], html='<h1>New Signature</h1><p>Please click <a href="' + url_for('show_draft', contract_id=contract_id, _external=True) + '">here</a> to view the contract.</p>')
    mail.send(msg)
    return redirect(url_for('index'))

from flask_mail import Message
from flask import flash, render_template, Response, redirect, url_for
from app import app, db, mail
from app.forms import LoginForm, RegistrationForm, CreateTemplateForm, CreateProposalForm
