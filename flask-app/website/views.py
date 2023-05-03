from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
#from .models import Post, User, Comment, Like
from . import dbobj
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
    fridgeIds = dbobj.getFridgesByUserID(userID=session['google_id'])
    fridges = [dbobj.getFridge(fridgeID=id) for id in fridgeIds]
    return render_template('home.html', fridges=fridges)



@views.route("/create-fridge", methods=['POST'])
@login_is_required
def create_fridge():
    text = request.form.get("fridge-name")
    dbobj.newFridge(ownerID=session['google_id'], fridgeName=text)
    return redirect('/home')

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


# @views.route("/search-recipes", methods=['POST', 'GET'])
# @login_is_required
# def search_recipes():
#     ingridientInput = request.args.get("search-input")
#     return 









@views.route("/fridge/", methods=['GET'])
@login_is_required
def fridge():
    fid = request.args.get('fid')
    fridge = dbobj.getFridge(fridgeID=fid)
    ingridientsArr = dbobj.getIngredientsInFridge(fridgeID=fid)
    session["currFridge"] = fid
    print("INGRIDIENTS: ", ingridientsArr)
    return render_template('fridge.html', ingridients=ingridientsArr, fridge=fridge)


@views.route("/add-ingridient", methods=['POST', 'GET'])
@login_is_required
def add_ingridient():
    itemName = request.args.get("item")
    quatityVal = request.args.get("quantityValue")
    quantityType = request.args.get("quantityType")
    expDate = request.args.get("expiration-date")
    location = request.args.get("location")
    fid = session["currFridge"]

    print("Item: ", itemName)
    print("QuantityV: ", quatityVal)
    print("QuantityT: ", quantityType)
    print("Date: ", expDate)
    print("Location: ", location)
    print("FID: ", fid)
    dbobj.addIngredientToFridge(fridgeID=fid, ingredientName=itemName, ingredientExpirationDate=expDate, ingredientQuatity=quatityVal, quantityUnits=quantityType, location=location)

    return redirect("/fridge/?fid="+str(fid))