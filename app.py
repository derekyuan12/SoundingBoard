import os
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import apology, login_required
from time import sleep

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///users.db")

# Create path to upload folder
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLD = 'static'
UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_FOLD)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Create new table for users 
db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, username TEXT NOT NULL, hash TEXT NOT NULL, bio TEXT, email TEXT, favorite TEXT, mostplayed TEXT, value_occurrence INTEGER, lastplayed TEXT, PRIMARY KEY (id))")
# Create new table for all sounds 
db.execute("CREATE TABLE IF NOT EXISTS sounds (sound_id INTEGER, name TEXT NOT NULL, filename TEXT NOT NULL, PRIMARY KEY (sound_id))")
# Create new table that tracks all play history
db.execute("CREATE TABLE IF NOT EXISTS plays (play_id INTEGER, sound_id INTEGER, user_id INTEGER, date_time DATETIME DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (play_id), FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (sound_id) REFERENCES sounds(sound_id))")

# Create a global variable to store the user's username
""" if session.get("user_id") is not None:
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]['username'] """


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/', methods=["GET", "POST"])
@login_required
def index():
    """Homepage"""

    # Create a variable to store the user's username. 
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]['username']

    # Create variables to store the most played sound on the entire website, and the number of plays
    mostplayed = db.execute(
        "SELECT sound_id, COUNT(sound_id) AS `value_occurrence` FROM plays GROUP BY sound_id ORDER BY `value_occurrence` DESC LIMIT 1")
    mostplayedsound = db.execute("SELECT name FROM sounds WHERE sound_id = ?", mostplayed[0]['sound_id'])[0]['name']
    playtimes = mostplayed[0]['value_occurrence']

    # Render the index page
    return render_template('index.html', username=username, mostplayedsound=mostplayedsound, playtimes=playtimes)


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    """ Allow the user to change their password """
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]['username']
    # If a post request is received
    if request.method == "POST":

        # Check to make sure all fields are filled out
        if request.form.get("current password") == "" or request.form.get("new password") == "" or request.form.get("new password confirmed") == "":
            return apology("All fields must be filled out")

        # Check to make sure the submitted current password matches the password in the database
        elif not check_password_hash(db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])[0]["hash"], request.form.get("current password")):
            return apology("Wrong current password")

        # Check to make sure both submitted passwords match
        elif request.form.get("new password") != request.form.get("new password confirmed"):
            return apology("New passwords don't match")

        else:
            # Hash the new password for security 
            hash = generate_password_hash(request.form.get("new password"), method='pbkdf2:sha256', salt_length=8)

            # Replace the old password with the new password in the SQL database
            db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, session["user_id"])

            # Render changepasswordsuccess.html, informing the user their password has been changed successfully
            return render_template("changepasswordsuccess.html", username=username)

    # If a get request is received
    else:

        # Render changepassword.html
        return render_template("changepassword.html", username=username)


@app.route("/changeemail", methods=["GET", "POST"])
@login_required
def changeemail():
    """Change the user's email"""

    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]['username']
    email = db.execute("SELECT email FROM users WHERE id = ?", session["user_id"])[0]["email"]
    if request.method == "POST":

        # Make sure all fields are filled out
        if request.form.get("current email") == "" or request.form.get("new email") == "" or request.form.get("new email confirmed") == "":
            return apology("All fields must be filled out")

        # Check to make sure current email matches email in table
        elif request.form.get("current email") != email:
            return apology("Wrong current email")

        # Check to make sure both submitted emails match
        elif request.form.get("new email") != request.form.get("new email confirmed"):
            return apology("New emails don't match")

        # Check to make sure the new email is not already taken
        elif db.execute("SELECT * FROM users WHERE email = ?", request.form.get("new email")):
            return apology("Email has already been taken")

        else:
            # Replace the old email with the new email in the SQL database
            db.execute("UPDATE users SET email = ? WHERE id = ?", request.form.get("new email"), session["user_id"])

            # Render the successful template
            return render_template("changeemailsuccess.html", username=username)

    # If a get request is received
    else:

        # Render changepassword.html
        return render_template("changeemail.html", username=username)


@app.route("/history", methods=["GET"])
@login_required
def history():
    """Show history of plays from the user"""

    # Create a variable to store all of the transaction info from the transactions table which will be displayed in history
    history = db.execute(
        "SELECT name, date_time FROM plays JOIN sounds ON plays.sound_id = sounds.sound_id WHERE user_id = ? ORDER BY date_time DESC", session["user_id"])

    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]['username']
    # Render history.html, passing in history
    return render_template("history.html", history=history, username=username)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
    

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    # Use SQL queries to obtain relevant data.
    users = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    username = users[0]["username"]
    sounds = db.execute("SELECT name FROM sounds")

    # If we receive a post request
    if request.method == "POST":
        # Update sounds and bio only if something is inputted into those fields, otherwise keep it same as before
        if request.form.get("sounds"):
            db.execute("UPDATE users SET favorite = ? WHERE id = ?", request.form.get("sounds"), session["user_id"])
        if request.form.get("bio"):
            db.execute("UPDATE users SET bio = ? WHERE id = ?", request.form.get("bio"), session["user_id"])

        # We have to recreate the users table with the updated bio and favorite
        users = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        return render_template("profile.html", users=users, username=username, sounds=sounds)
    return render_template("profile.html", users=users, username=username, sounds=sounds)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # If a post request is received
    if request.method == "POST":

        # Check to make sure the username field was not blank
        if request.form.get("username") == "":
            return apology("Username is blank")

        # Check to make sure the password field was not blank
        elif request.form.get("password") == "":
            return apology("Password is blank")

        # Check to make sure the email field was not blank
        if request.form.get("email") == "":
            return apology("Email is blank")

        # Check to make sure both submitted passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords don't match")

        # Check to make sure the username does not already exist
        elif db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username")):
            return apology("Username is already taken")

        # Check to make sure the email is not already taken
        elif db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email")):
            return apology("Email has already been taken")

        else:
            # Hash the password for security 
            hash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

            # Add the new username, email, and password into the SQL database
            db.execute("INSERT INTO users (username, hash, email) VALUES (?, ?, ?)", 
                       request.form.get("username"), hash, request.form.get("email"))

            # Set the session id to keep the user logged in
            session["user_id"] = db.execute("SELECT id FROM users WHERE username = ?", request.form.get("username"))[0]["id"]

            username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]['username']
            # Redirect to homepage upon registering and logging in
            return render_template("registered.html", username=username)

    # If a get request is received
    else:

        # Render register.html
        return render_template("register.html")


@app.route("/social", methods=['GET', 'POST'])
@login_required
def social():
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]['username']

    # If we receive a post request
    if request.method == "POST":
        # Find user information for user where username is equal to the username that was clicked because that's the profile we want
        users = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # Go to the profile of that user
        return render_template("otherprofile.html", users=users, username=username)

    # If we receive a get request
    else:
        # Display information of all users
        users = db.execute("SELECT * FROM users")
        return render_template("social.html", users=users, username=username)


@app.route("/soundboard", methods=['GET', 'POST'])
@login_required
def soundboard():
    # Create a variable to store all sounds in the database
    sounds = db.execute("SELECT * FROM sounds")

    # Create a variable to store the user's username
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]['username']

    # If a post request is received
    if request.method == 'POST':
        # Determine the value of the sound name
        clicked = request.form["submit_button"]

        # Find the sound_id of the sound that was clicked and insert this and user id into plays
        newsound_id = db.execute("SELECT sound_id FROM sounds WHERE name = ?", clicked)[0]['sound_id']
        db.execute("INSERT INTO plays (sound_id, user_id) VALUES (?, ?)", newsound_id, session["user_id"])
        
        name = db.execute("SELECT name FROM sounds WHERE sound_id = ?", newsound_id)[0]['name']

        # Find the current most played sound by finding the sound_id with the most occurrences in plays
        mostplayed = db.execute(
            "SELECT sound_id, COUNT(sound_id) AS `value_occurrence` FROM plays WHERE user_id = ? GROUP BY sound_id ORDER BY `value_occurrence` DESC LIMIT 1", session["user_id"])
       
        # Translate sound_id of mostplayed to sound name
        song = db.execute("SELECT name FROM sounds WHERE sound_id = ?", mostplayed[0]["sound_id"])[0]["name"]

        # Update the users table with the current user's most updated values for mostplayed, times mostplayed has been played, and the last played song
        db.execute("UPDATE users SET mostplayed = ?, value_occurrence = ?, lastplayed = ? WHERE id = ?", 
                   song, mostplayed[0]['value_occurrence'], name, session["user_id"])
        
        # We sleep the function for a large number of seconds because otherwise the page automatically refreshes when we send a post request, which disrupts the audio.
        # We tried fixing this with AJAX requests but after several hours of failed implementation, we decided that the sleep function would work best for our purposes.
        sleep(100000)
        return render_template("soundboard.html", sounds=sounds, username=username)

    if request.method == 'GET':
        return render_template("soundboard.html", sounds=sounds, username=username)


@app.route("/uploaded", methods=["GET", "POST"])
@login_required
def uploaded():
    # Create a variable to store the user's username
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]['username']

    if request.method == 'POST':
        # Obtain the file and save it with the correct path defined above
        f = request.files['file']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        
        # Create filename so that it links correctly to the right location in the static folder
        file_name = "'../static/" + f.filename + "'"

        # Insert the new sound and the filename into the sounds table
        db.execute("INSERT INTO sounds (name, filename) VALUES (?, ?)", request.form.get("name"), file_name)
        
        # Use SQL query to get updated sounds table
        sounds = db.execute("SELECT * FROM sounds")
        return render_template("soundboard.html", username=username, sounds=sounds)
    return render_template("audio.html", username=username)


@app.route('/audio', methods=["GET"])
@login_required
def upload_file():
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]['username']
    return render_template('audio.html', username=username)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

