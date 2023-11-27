from flask import render_template, request, redirect, url_for, session, make_response, Response
from app import app, db
from app.models import User, Twibbon
from datetime import datetime
from PIL import Image
import hashlib, os, imghdr ,requests

def randomfilename():
    name = str(datetime.today().isoformat())
    name = hashlib.md5((name.encode()))
    name = name.hexdigest()
    return str(name)

def encrypt_password(password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password


@app.route('/login', methods=['POST'])
def login():
    if 'username' in session:
        username = session['username']
        return redirect(url_for('kreator_user(username)'))
    elif request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        hashed_password = encrypt_password(password)
        user = User.query.filter_by(username=username,password=hashed_password).first()
        if user is not None:
            # login successful
            session['username'] = username
            return redirect(url_for('kreator_user', username=username))
        else:
            return render_template('kreator.html', title='Log in | Kreator',loginalertdanger='Username atau Password Salah !!!')
    else:
        return redirect(url_for('kreator'))

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        user_with_same_username = User.query.filter_by(username=request.form['username']).first()
        user_with_same_email = User.query.filter_by(email=request.form['email']).first()

        if user_with_same_username is not None or user_with_same_email is not None:
            return render_template('kreator.html', title='Log in | Kreator',registeralertdanger='Username atau email sudah ada !!!')

        # Encrypt the password
        hashed_password = encrypt_password(request.form['password'])

        # Create a new user
        new_user = User(username=request.form['username'], email=request.form['email'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Create path upload twibbon
        user_folder=request.form['username']
        path_twb = os.environ.get('PATH_TWIBBON')
        os.system('mkdir '+path_twb+'/'+user_folder)
        return render_template('kreator.html', title='Log in | Kreator',registeralertprimary='Silahkan Login !!!')
    else:
        return redirect(url_for('kreator'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('kreator'))