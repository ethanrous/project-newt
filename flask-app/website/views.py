from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
#from .models import Post, User, Comment, Like
from . import dbobj
#from auth import login_is_required
from flask import Flask, session, abort, redirect, request
from itertools import chain

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
    fridgeIds = dbobj.getFridgesByUserID(userID=session['google_id'])
    fridges = [dbobj.getFridge(fridgeID=id) for id in fridgeIds]

    allIngridients = []
    for fridge in fridges:
        ingArr = fridge['ingredients']
        fName = fridge['fridgeName']
        for ing in ingArr:
            finalIng = {}
            finalIng['ingredientName'] = ing['ingredientName']
            finalIng['fridgeName'] = fName
            finalIng['expDate'] = ing['ingredientExpirationDate']
            allIngridients.append(finalIng)
    
    allIngridients.sort(key=lambda item:item['expDate'])
    print(allIngridients)

    return render_template('notifications.html', ingridients=allIngridients)

@views.route("/recipes", methods=['GET'])
@login_is_required
def recipes():
    return render_template('recipes.html')

@views.route("/fridge/", methods=['GET'])
@login_is_required
def fridge():
    fid = request.args.get('fid')
    fridge = dbobj.getFridge(fridgeID=fid)
    ingridients = dbobj.getIngredientsInFridge(fridgeID=fid)
    session["currFridge"] = fid
    collaboratorsID = dbobj.getFridgeCollaborators(fridgeID=fid)
    collaboratorsContactInfo = [dbobj.getUserContactByUserID(c) for c in collaboratorsID]
    for ingridient in ingridients:
        ingridient['nutrition'] = (dbobj.getIngredientDataFromName(ingredientName=ingridient['ingredientName']))[1]

    return render_template('fridge.html', ingridients=ingridients, fridge=fridge, collaborators=collaboratorsContactInfo)


@views.route("/add-ingridient", methods=['POST', 'GET'])
@login_is_required
def add_ingridient():
    itemName = request.args.get("item")
    quatityVal = request.args.get("quantityValue")
    quantityType = request.args.get("quantityType")
    expDate = request.args.get("expiration-date")
    location = request.args.get("location")
    fid = session["currFridge"]
    dbobj.addIngredientToFridge(fridgeID=fid, ingredientName=itemName, ingredientExpirationDate=expDate, ingredientQuatity=quatityVal, quantityUnits=quantityType, location=location)
    #print(dbobj.getIngredientDataFromName(ingredientName=itemName))

    return redirect("/fridge/?fid="+str(fid))

@views.route("/share-fridge", methods=['POST'])
@login_is_required
def share_fridge():
    collaboratorEmail = request.form.get("share-email")
    collaboratorID = dbobj.getUserIDFromEmail(collaboratorEmail)
    fid = session["currFridge"]

    if dbobj.userExists(collaboratorID):
        dbobj.shareFridgeWithUser(collaboratorID, fid)

    return redirect("/fridge/?fid="+str(fid))