from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin

import raspberry

#region --- globals

app = Flask(__name__)

app.config['SECRET_KEY'] = 'place_your_secret_here'
app.config['SECURITY_PASSWORD_SALT'] = 'place_your_password_salt_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'login.html'
app.config['SECURITY_LOGIN_URL'] = '/auth.login'

db = SQLAlchemy(app)

roles_users = db.Table('roles_users', db.Column('user_id', db.Integer, db.ForeignKey('user.id')), db.Column('role_id', db.Integer, db.ForeignKey('role.id')))

#endregion

#region --- class definitions

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True)
    description = db.Column(db.String(255))

#endregion

#region --- function definitions


#endregion

#region --- script

#setup flask security

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

#setup authorization blueprints
from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

#setup api
from main import main as main_blueprint
app.register_blueprint(main_blueprint)

#setup GPIO
raspberry.setup()
