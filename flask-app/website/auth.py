#from config import GOOGLE_CLIENT_ID
import os
import pathlib
import requests
from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import dbobj
import time
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

#from .models import User
# from flask_login import login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint("auth", __name__)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

client_secrets_file = os.path.join(pathlib.Path(__file__).parent.parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@auth.route("/login", methods = ['POST', 'GET'])
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@auth.route("/callback", methods = ['POST', 'GET'])
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    time.sleep(1)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )



    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")

    userExists = dbobj.doesUserExist(userID=session['google_id'])
    print("UserExists: ", userExists)
    if not userExists:
        dbobj.newUser(session["google_id"], session["name"], session["email"])

    return redirect('/home')


@auth.route("/logout", methods = ['POST', 'GET'])
def logout():
    session.clear()
    return redirect("/")


@auth.route("/")
def index():
    return render_template("landing.html")

