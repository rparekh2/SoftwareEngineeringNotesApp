# FLASK Tutorial 1 -- We show the bare bones code to get an app up and running

# imports
import os                 # os is used to get environment variables IP & PORT

import bcrypt
from flask import Flask   # Flask is the web app that we will customize
from flask import render_template
from flask import request
from flask import redirect, url_for
from database import db
from models import Note as Note
from models import User as User
from flask import session
from models import Comment as Comment
from forms import RegisterForm, LoginForm, CommentForm

app = Flask(__name__)     # create an app

app.config['SECRET_KEY'] = 'SE3155'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_note_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
#  Bind SQLAlchemy db object to this Flask app
db.init_app(app)
# Setup models
with app.app_context():
    db.create_all()   # run under the app context


notes = {1: {'title': 'First note', 'text': 'This is my first note', 'date': '10-1-2020'},
             2: {'title': 'Second note', 'text': 'This is my second note', 'date': '10-2-2020'},
             3: {'title': 'Third note', 'text': 'This is my third note', 'date': '10-3-2020'}
             }
# @app.route is a decorator. It gives the function "index" special powers.
# In this case it makes it so anyone going to "your-url/" makes this function
# get called. What it returns is what is shown as the web page

# Home page
@app.route('/')
@app.route('/index')
def index():
    # check if a user is saved in session
    if session.get('user'):
        return render_template("index.html", user=session['user'])
    return render_template("index.html")

# List of notes
@app.route('/notes')
def get_notes():
    # check if a user is saved in session
    if session.get('user'):
        # retrieve notes from database
        my_notes = db.session.query(Note).filter_by(user_id=session['user_id']).all()

        return render_template('notes.html', notes=my_notes, user=session['user'])
    else:
        # user is not in session redirect to login
        return redirect(url_for('login'))

# Specific note
@app.route('/notes/<note_id>')
def get_note(note_id):
    # check if a user is saved in session
    if session.get('user'):
        # retrieve singular note from database
        my_note = db.session.query(Note).filter_by(id=note_id, user_id=session['user_id']).one()

        # create a comment form object
        form = CommentForm()

        return render_template('note.html', note=my_note, user=session['user'], form=form)
    else:
        # user is not in session redirect to login
        return redirect(url_for('login'))

# Create new note
@app.route('/notes/new', methods=['GET', 'POST'])
def new_note():
    # check if a user is saved in session
    if session.get('user'):
        # check method used for request
        if request.method == 'POST':
            # get title data
            title = request.form['title']
            # get note data
            text = request.form['noteText']
            #create timestamp
            from datetime import datetime
            today = datetime.today()
            # format date/time mm/dd/yyyy, H/M/S
            today = today.strftime("%m-%d-%Y, %H:%M:%S")
            new_record = Note(title, text, today, session['user_id'])
            # add note to database
            db.session.add(new_record)
            db.session.commit()

            return redirect(url_for('get_notes'))
        else:
            # GET request - show new note form
            return render_template('new.html', user=session['user'])
    else:
        # user is not in session redirect to login
        return redirect(url_for('login'))

# Edit Note
@app.route('/notes/edit/<note_id>', methods = ['GET', 'POST'])
def update_note(note_id):
    # check if a user is saved in session
    if session.get('user'):
        # check method used for request
        if request.method == 'POST':
            # get title data
            title = request.form['title']
            # get note data
            text = request.form['noteText']
            note = db.session.query(Note).filter_by(id=note_id).one()
            # update note data
            note.title = title
            note.text = text
            # update note in DB
            db.session.add(note)
            db.session.commit()

            return redirect(url_for('get_notes'))
        else:
            # GET request
            # retrieve note from database
            my_note = db.session.query(Note).filter_by(id=note_id).one()

            return render_template('new.html', note=my_note, user=session['user'])
    else:
        # user is not in session redirect to login
        return redirect(url_for('login'))

# Delete Note
@app.route('/notes/delete/<note_id>', methods = ['POST'])
def delete_note(note_id):
    # check if a user is saved in session
    if session.get('user'):
        # retrieve note from database
        my_note = db.session.query(Note).filter_by(id=note_id).one()

        # delete note from database
        db.session.delete(my_note)
        db.session.commit()

        return redirect(url_for('get_notes'))
    else:
        # user is not in session redirect to login
        return redirect(url_for('login'))

# Sorting all notes by Title
@app.route('/notes/sortTitle_notes', methods=['POST'])
def sortTitle_notes():
    # check if a user is saved in session
    if session.get('user'):
        # access database and sort Note table by title field
        my_notes = db.session.query(Note).order_by(Note.title)

        return render_template('notes.html', notes=my_notes, user=session['user'])
    else:
        # user is not in session redirect to login
        return redirect(url_for('login'))

# Sorting all notes by Date/Time
@app.route('/notes/sortDate_notes', methods=['POST'])
def sortDate_notes():
    # check if a user is saved in session
    if session.get('user'):
        # access database and sort Note table by date field in descending order
        my_notes = db.session.query(Note).order_by(Note.date.desc())

        return render_template('notes.html', notes=my_notes, user=session['user'])
    else:
        # user is not in session redirect to login
        return redirect(url_for('login'))

# Search notes
@app.route('/notes/search_notes', methods=['POST'])
def search_notes():
    # check if a user is saved in session
    if session.get('user'):
        # access database and search Note table to see if it contains value from search bar
        my_notes = db.session.query(Note).filter(Note.title.like('%' + request.form['search'] + '%'))

        return render_template('notes.html', notes=my_notes, user=session['user'])
    else:
        # user is not in session redirect to login
        return redirect(url_for('login'))

# Register for account
@app.route('/register', methods=['POST', 'GET'])
def register():
        form = RegisterForm()
        # validate_on_submit only validates using POST
        if form.validate_on_submit():
            # form validation included a criteria to check the username does not exist
            # we can know we are safe to add the user to the database
            password_hash = bcrypt.hashpw(
                request.form['password'].encode('utf-8'), bcrypt.gensalt()
            )
            first_name = request.form['firstname']
            last_name = request.form['lastname']
            new_record = User(first_name, last_name, request.form['email'], password_hash)
            db.session.add(new_record)
            db.session.commit()
            # save the user's name to the session
            session['user'] = first_name
            the_user = db.session.query(User).filter_by(email=request.form['email']).one()
            session['user_id'] = the_user.id

            return redirect(url_for('get_notes'))
        return render_template('register.html', form=form)

# Login to account
@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form['email']).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = the_user.first_name
            session['user_id'] = the_user.id
            # render view
            return redirect(url_for('get_notes'))

        # password check failed
        # set error message to alert user
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)

# Logout of account
@app.route('/logout')
def logout():
    # check if a user is saved in session
    if session.get('user'):
        session.clear()

    return redirect(url_for('index'))

# Create comment
@app.route('/notes/<note_id>/comment', methods=['POST'])
def new_comment(note_id):
    # check if a user is saved in session
    if session.get('user'):
        comment_form = CommentForm()
        # validate_on_submit only validates using POST
        if comment_form.validate_on_submit():
            # get comment data
            comment_text = request.form['comment']
            new_record = Comment(comment_text, int(note_id), session['user_id'])
            db.session.add(new_record)
            db.session.commit()

        return redirect(url_for('get_note', note_id=note_id))

    else:
        # user is not in session redirect to login
        return redirect(url_for('login'))

# Delete comment
@app.route('/notes/delete_comment/<comment_id>', methods=['POST'])
def delete_comment(comment_id):
    # check if a user is saved in session
    if session.get('user'):
        # Retrieve comment from database
        my_comment = db.session.query(Comment).filter_by(id=comment_id).one()
        # delete comment from database
        db.session.delete(my_comment)
        db.session.commit()

        return redirect(url_for('get_notes'))
    else:
        # user is not in session redirect to login
        return redirect(url_for('login'))

# Edit comment
@app.route('/notes/editComment/<comment_id>', methods = ['GET','POST'])
def update_comment(comment_id):
    # check if a user is saved in session
    if session.get('user'):
        # check method used for request
        if request.method == 'POST':
            # get comment data
            text = request.form['commentText']
            comment = db.session.query(Comment).filter_by(id=comment_id).one()
            # update comment data
            comment.content = text
            # update comment in DB
            db.session.add(comment)
            db.session.commit()

            return redirect(url_for('get_notes'))
        else:
            # GET request - show new comment form to edit comment
            # retrieve comment from database
            my_comment = db.session.query(Comment).filter_by(id=comment_id).one()

            return render_template('new_comment.html', comment=my_comment, user=session['user'])
    else:
        # user is not in session redirect to login
        return redirect(url_for('login'))



app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)

# To see the web page in your web browser, go to the url,
#   http://127.0.0.1:5000

# Note that we are running with "debug=True", so if you make changes and save it
# the server will automatically update. This is great for development but is a
# security risk for production.
