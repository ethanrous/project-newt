from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
#from .models import Post, User, Comment, Like
from . import db
#from auth import login_is_required
from flask import Flask, session, abort, redirect, request

views = Blueprint("views", __name__)

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()
    wrapper.__name__ = function.__name__
    return wrapper


@views.route("/home")
@login_is_required
def protected_area():
    print("**********LOOOK HERE************")
    print(session)
    return render_template('home.html')

@views.route("/settings")
@login_is_required
def settings():
    return render_template('settings.html')

@views.route("/notifications")
@login_is_required
def notifications():
    return render_template('notifications.html')

@views.route("/recipes", methods=['GET'])
@login_is_required
def recipes():
    return render_template('recipes.html')

@views.route("/fridge", methods=['GET'])
@login_is_required
def fridge():
    return render_template('fridge.html')