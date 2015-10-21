"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template('homepage.html')


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/signup')
def show_signup():
    """Show sign-up form."""

    return render_template('signup.html')


@app.route('/process-signup', methods=["POST"])
def process_signup():
    """Process sign-up form. Check if user in database, add if not."""

    email = request.form.get('email')
    password = request.form.get('password')

    account = User.query.filter_by(email=email).first()

    # if account is None:
    #     add email and password to database
            # make instance of user class with email and password
            # add to session
            # commit
    # else:
    #     check if password and email match

    if account is None:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("You created an account. Please login.")
    else:
        flash("You already have an account. Please login")
    return redirect('/login')
    

@app.route('/login')
def show_login():
    """Show login form."""
    if 'user' in session:
        flash('You are already logged in')
    return render_template('login.html')

@app.route('/process-login', methods=["POST"])
def process_login():
    """Process login form. Check if user and email match"""
    # Would be good to check if in database first, and if not, reroute to /signup

    email = request.form.get('email')
    password = request.form.get('password')

   
    account = User.query.filter_by(email=email).first()

    if account.password == password:
        flash('You were successfully logged in')
        session['user'] = email
        return render_template('homepage.html')
    #put in else

@app.route('/logout')
def process_logout():
    """Remove user from session"""
    print session.get('user')
    removed =  session.pop('user')
    print removed
    flash('You have successfully logged out.')

    return render_template('homepage.html')

# @app.route('users/<int:user_id>')
# def user_info():
#     pass

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()