from cs50 import SQL
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from helpers import *
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from twilio.rest import Client

#from time import gmtime, strftime


# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///doey.db")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    #get username of current session
    userdets =  db.execute("SELECT * FROM users WHERE id = :uid", uid=session["user_id"])
    curr_email= userdets[0]["email"]
    return render_template('index.html',name=userdets[0]["name"])


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("phone"):
            return apology("must provide phone")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE phone = :phone", phone=request.form.get("phone"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["password"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # ensure user enters a Username
        if not request.form.get("name"):
            return apology("must provide name")

        if not request.form.get("phone"):
            return apology("must provide phone")

        #   ensure user enters a new email
        if db.execute("SELECT * FROM users WHERE phone = :phone", phone=request.form.get("phone")):
            return apology("phone is already registered")

        # ensure password is entered
        elif not request.form.get("password"):
            return apology("must provide password")

        # ensure password is confirmed correctly
        elif not request.form.get("confirm_passwd") or request.form.get("confirm_passwd")!=request.form.get("password") :
            return apology("please confirm correct password")

        name = request.form.get("name")
        email = request.form.get("email")
        hash1 = pwd_context.hash(request.form.get("password"))
        phone = str(request.form.get("phone"))
        #insert values into database
        rows = db.execute("INSERT INTO users (name,phone,email,password) VALUES(:name,:phone,:email,:hash)",name=name,phone=phone,email=email,hash=hash1)
        # redirect user to home page
        account_sid = "AC6b4bcf83b25c19054e9f9df4b3380e9b"
        # Your Auth Token from twilio.com/console
        auth_token  = "41e0689bb9f74ca278d9dc2ce47395c8"
        #client = Client(account_sid, auth_token)

        client = Client(account_sid, auth_token)

            message = client.messages.create(
            to="+31614657384",
        from_="+3197014200259",
            body="Thanks for registering with Insur. Your insurance info will be sent via SMS regularly. For more details call +180 555 555 !")

        #print(message.sid)

        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/sms", methods=["GET", "POST"])
def sms():
    # Your Account SID from twilio.com/console
    account_sid = "AC6b4bcf83b25c19054e9f9df4b3380e9b"
    # Your Auth Token from twilio.com/console
    auth_token  = "41e0689bb9f74ca278d9dc2ce47395c8"
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to="+31614657384",
    from_="+3197014200259",
        body="Hello from Insur! Buy Crop seeds from Generic Seeds @ 20% discount with our COUPON: 4X1ER !, ")

    #print(message.sid)
    print('message')
    return redirect(url_for('index'))

if __name__=='__main__':
    app.run(debug=True)