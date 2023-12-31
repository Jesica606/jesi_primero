import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')




@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']


        db = get_db()
        error = None

        if not username:
            error = 'El Nombre de Usuario es requiredo.'

        elif not email:
            error = 'El Email es requiredo.'
        
        elif not password:
            error = 'La Contraseña es requiredo.'
        elif not password2:
            error = 'Verificar la Contraseña es requiredo.'
        elif not password == password2:
            error = 'Error de Verificacion.'



        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, email) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), email)
                )
                db.commit()
            except db.IntegrityError:
                error = f"El Nombre de Usuario {username} ya esta registrado."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')




@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Nombre de Usuario Incorrecto.'
        elif not check_password_hash(user['password'], password):
            error = 'Contraseña Incorrecto.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')



@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()




@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/email', methods=('GET', 'POST'))
@login_required
def cambiaremail():
   if request.method == 'POST':
       email2 = request.form['email2']
       error = None

       if not email2:
           error = 'Email requerido.'
       if error is not None:
           flash(error)
       else:
           db = get_db()
           db.execute(
               'UPDATE user SET email = ?'
               ' WHERE id = ?',
               (email2, g.user["id"])
           )
           db.commit()
           return redirect(url_for('blog.index'))
   return render_template('auth/email.html')