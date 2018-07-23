from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import re

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
        return '<User {}>'.format(self.username)

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

    def parse_party_tags(self):
        parties = []
        for text in [self.code, self.body]:
            for line in text.split("\n"):
                regex = re.compile('\[\[\s*[Pp][Aa][Rr][Tt][Yy]\s*:\s*([a-zA-Z0-9 _]+)\s*\]\]')
                m = regex.match(line)
                if m:
                    parties.append(m.group(0).strip())
        return parties

    def __repr__(self):
        return '<Template {}:{}:{}>'.format(User.query.get(self.owner_id).username, self.title, self.id)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'), index=True)

    def __repr__(self):
        return '<Role {}:{}'.format(self.id, self.name)

class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'), index=True)
    params = db.Column(db.TEXT)
    status = db.Column(db.String(32), index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)

    def __repr__(self):
        return '<Contract {}:{}:{}>'.format(User.query.get(self.owner_id).username, Template.query.get(self.template_id).title, self.id)

class Party(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), index=True)
    role = db.Column(db.Integer, db.ForeignKey('role.id'), index=True)
    party_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    signed_on = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Party {}:{}:{}>'.format(self.contract_id, self.role, User.query.get(self.owner_id).username)
