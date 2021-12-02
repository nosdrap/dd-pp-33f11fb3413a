from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('scheduler', __name__)

import datetime
from io import BytesIO


@bp.route('/')
@login_required
def index():
    db = get_db()
    tasks = db.execute(
        'SELECT p.id, title, deadline, author_id, username, finished'
        ' FROM tasks p JOIN user u ON p.author_id = u.id'
        ' ORDER BY deadline ASC'
    ).fetchall()
    now =datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
    maxtime = datetime.datetime.strptime("9999-12-31 23:59:59", "%Y-%m-%d %H:%M:%S")
    return render_template('scheduler/index.html', tasks=tasks, now=now, maxtime=maxtime)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        deadline = request.form['deadline']
        if deadline:
            deadline = deadline.replace("T"," ")+":00"
        error = None
        file = request.files['inputFile']
        filename = file.filename
        filedata = file.read()

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            if deadline:
                db.execute(
                    'INSERT INTO tasks (title, body, author_id, finished, deadline, filename, filedata)'
                    ' VALUES (?, ?, ?, 0, ?, ?, ?)',
                    (title, body, g.user['id'], deadline, filename, filedata)
                )
            else:
                db.execute(
                    'INSERT INTO tasks (title, body, author_id, finished, filename, filedata, deadline)'
                    ' VALUES (?, ?, ?, 0, ?, ?, ?)',
                    (title, body, g.user['id'], filename, filedata, datetime.datetime.strptime("9999-12-31 23:59:59", "%Y-%m-%d %H:%M:%S"))
                )
            db.commit()
            return redirect(url_for('scheduler.index'))

    return render_template('scheduler/create.html')
    
@bp.route('/<int:id>/delete')
@login_required
def delete(id):
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('scheduler.index'))

@bp.route('/<int:id>/finish')
@login_required
def finish(id):
    db = get_db()
    db.execute('UPDATE tasks SET FINISHED = 1 WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('scheduler.index'))

@bp.route('/<int:id>/view')
@login_required
def view(id):
    db = get_db()
    task = db.execute(
        'SELECT p.id, title, deadline, author_id, username, finished, body, filename'
        ' FROM tasks p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',(id,)
    ).fetchone()
    now =datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
    maxtime = datetime.datetime.strptime("9999-12-31 23:59:59", "%Y-%m-%d %H:%M:%S")
    return render_template('scheduler/view.html', task=task, now=now, maxtime=maxtime)

@bp.route('/finished')
@login_required
def finished():
    db = get_db()
    tasks = db.execute(
        'SELECT p.id, title, deadline, author_id, username, finished'
        ' FROM tasks p JOIN user u ON p.author_id = u.id'
        ' ORDER BY deadline ASC'
    ).fetchall()
    return render_template('scheduler/finished.html', tasks=tasks)


@bp.route('/<int:id>/download')
@login_required
def download(id):
    db = get_db()
    file = db.execute(
        'SELECT filename, filedata'
        ' FROM tasks p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',(id,)
    ).fetchone()
    return send_file(BytesIO(file['filedata']),attachment_filename=file['filename'],as_attachment=True)