from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import re, json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}:{}>'.format(self.username, self.email)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True, nullable=False)
    code = db.Column(db.TEXT)
    body = db.Column(db.TEXT)
    party_labels = db.Column(db.TEXT)
    params = db.Column(db.TEXT)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    owner = db.relationship('User', backref='template')

    def get_party_labels(self):
        return json.loads(self.party_labels)

    def get_params(self):
        return json.loads(self.params)

    def __repr__(self):
        return '<Template {}:{}:{}>'.format(User.query.get(self.owner_id).username, self.title, self.id)

class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'), index=True)
    memo = db.Column(db.TEXT)
    params = db.Column(db.TEXT)
    status = db.Column(db.String(32), index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('contract.id'), index=True, nullable=True)
    owner = db.relationship('User', backref='contract')
    template = db.relationship('Template', backref='contract')

    def __repr__(self):
        return '<Contract {}:{}:{}:{}>'.format(self.id, User.query.get(self.owner_id).username, self.memo, self.status)

class Party(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), index=True)
    role = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    signed_on = db.Column(db.DateTime, nullable=True)
    contract = db.relationship('Contract', backref='party')
    user = db.relationship('User', backref='party')

    def __repr__(self):
        return '<Party {}:{}:{}:{}>'.format(self.contract_id, self.role, User.query.get(self.user_id).username, self.signed_on)

