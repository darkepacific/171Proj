from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, SelectField, RadioField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask (__name__)
app.secret_key='secret123'
app.debug = True

#   MySQL will likely be changed this is just temporary
# Server Registeration Data Will Go Here
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)


Articles = Articles()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/guess')
def guess():
    return render_template('guess.html')

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/jokes')
def jokes():
    return render_template('jokes.html')

@app.route('/example')
def artciles():
    return render_template('example.html', articles = Articles)

GENDERS = ('Male', 'Female', 'Other')
MAJORS = ('Computer Science/CSE/ECE', 'Statistics', 'Math', 'Physics', 'Other')
MUSIC_GENRES = ('Rock', 'Hip-Hop', 'Rap', 'Country', 'Pop', 'EDM')
MOVIE_GENRES = ('Thriller', 'Horror', 'Action', 'Superhero', 'Mystery', 'Comedy', 'Romantic Comedy', 'SciFi', 'Documentary', 'Indie', 'Family')
JOKE_GENRES = ('Medicine', 'Politics', 'Programming', 'Sports', 'Kids', 'School', 'Animal', 'Law', 'Math', 'Nerd', 'Other')
JOKE_TYPES = ('Puns', 'Question', 'One-Liner', 'Dialogue', 'Pick-up Line', 'Punch Line', 'Fun Fact')

class RegisterForm(Form):
    userID = StringField('User ID', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])

    age = StringField('Age', [validators.Length(min=1, max=2)])
    #Added forms
    gender = SelectField('Gender', choices=[(gender, gender) for gender in GENDERS])

    major = SelectField('Major', choices=[(major, major) for major in MAJORS])

    joke_genre = SelectField('Prefered Joke Genre', choices=[(jokegenre, jokegenre) for jokegenre in JOKE_GENRES])

    joke_type = SelectField('Favorite Joke Type', choices=[(joketype, joketype) for joketype in JOKE_TYPES])

    music_genre = SelectField('Favorite Music Genres', choices=[(genre, genre) for genre in MUSIC_GENRES])

    movie_genre = SelectField('Favorite Movie Genres', choices=[(genre, genre) for genre in MOVIE_GENRES])






    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# User RegisterFormer
############
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        gender = form.gender.data
        joke_type = form.joke_type.data
        music_genre = form.music_genre.data

        password = sha256_crypt.encrypt(str(form.password.data))

          # Create Cursor
        cur = mysql.connection.cursor()

        #Execute Query
        cur.execute("INSERT INTO users(name, email, username, gender, music_genre, joke_type, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('You are now registered','success')

        redirect(url_for('/login'))
        return redirect(url_for('/login'))
    # If method is GET, serve the form to be filled
    return render_template('register.html', form=form)

# User login
############
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
