from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html')

@views.route('/fridges')
def home():
    return render_template('fridges.html')

@views.route('/recipes')
def home():
    return render_template('recipes.html')

@views.route('/settings')
def home():
    return render_template('settings.html')

@views.route('/notifications')
def home():
    return render_template('notifications.html')