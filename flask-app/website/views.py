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

    ownedFridgesID = dbobj.getOwnedFridgesByUserID(userID=session['google_id'])
    ownedFridges = [dbobj.getFridgeData(fridgeID=id) for id in ownedFridgesID]

    sharedFridgesID = dbobj.getCollabFridgesByUserID(userID=session['google_id'])
    sharedFridges = [dbobj.getFridgeData(fridgeID=id) for id in sharedFridgesID]
    return render_template('home.html', ownedFridges=ownedFridges, sharedFridges=sharedFridges)



@views.route("/create-fridge", methods=['POST'])
@login_is_required
def create_fridge():
    text = request.form.get("fridge-name")
    dbobj.newFridge(ownerID=session['google_id'], fridgeName=text)
    return redirect('/home')

@views.route("/settings")
@login_is_required
def settings():
    userContactInfo = dbobj.getUserContactByUserID(userID=session['google_id'])
    return render_template('settings.html', userName=session['name'])

@views.route("/notifications")
@login_is_required
def notifications():
    fridgeIds = dbobj.getFridgesByUserID(userID=session['google_id'])
    fridges = [dbobj.getFridgeData(fridgeID=id) for id in fridgeIds]

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

    return render_template('notifications.html', ingridients=allIngridients)

@views.route("/recipes", methods=['GET'])
@login_is_required
def recipes():
    return render_template('recipes.html')

@views.route("/fridge/", methods=['GET'])
@login_is_required
def fridge():
    fid = request.args.get('fid')
    fridge = dbobj.getFridgeData(fridgeID=fid)

    if not dbobj.canUserAccessFridge(fid, session['google_id']) or fridge == None:
        return render_template('404.html'), 404

    ingridients = dbobj.getIngredientsInFridge(fridgeID=fid)
    session["currFridge"] = fid
    print('ingridients', ingridients)
    collaboratorsID = dbobj.getFridgeCollaborators(fridgeID=fid)
    collaboratorsArr = [dbobj.getUserContactByUserID(c) for c in collaboratorsID]
    collaboratorsContactInfo = list(filter(lambda item: item is not None, collaboratorsArr))

    for ingridient in ingridients:
        _, ingredientData = dbobj.getIngredientDataFromName(ingredientName=ingridient['ingredientName'])
        if ingredientData:
            ingridient['nutrition'] = ingredientData
        else:
            ingridient['nutrition'] = None
    return render_template('fridge.html', ingridients=ingridients, fridge=fridge, collaborators=collaboratorsContactInfo, isOwner=dbobj.doesUserOwnFridge(fid, session['google_id']))


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

    return redirect("/fridge/?fid="+str(fid))

@views.route("/share-fridge", methods=['POST'])
@login_is_required
def share_fridge():
    collaboratorEmail = request.form.get("share-email")
    collaboratorID = dbobj.getUserIDFromEmail(collaboratorEmail)
    fid = session["currFridge"]

    if dbobj.doesUserExist(collaboratorID) and collaboratorID not in dbobj.getFridgeCollaborators(fid) and collaboratorID != session['google_id']:
        dbobj.shareFridgeWithUser(collaboratorID, fid)

    return redirect("/fridge/?fid="+str(fid))


@views.route("/unshare-fridge/", methods=['GET','POST'])
@login_is_required
def unshare_fridge():

    collabEmail = request.args.get("collabEmail")
    if collabEmail != session['email']:
        collabID = dbobj.getUserIDFromEmail(collabEmail)
        fid = session["currFridge"]
        dbobj.unshareFridgeWithUser(userID=collabID, fridgeID=fid)


    return redirect("/fridge/?fid="+str(fid))


@views.route("/delete-fridge", methods=['GET','POST'])
@login_is_required
def delete_fridge():
    fid = session['currFridge']
    dbobj.deleteFridge(fid, session['google_id'])
    print("delted the fridge")
    return redirect("/home")


@views.route("/change-name", methods=['GET','POST'])
@login_is_required
def change_name():
    name = request.form.get('name')
    dbobj.updateUserName(userID=session['google_id'],newName=name)
    session['name'] = name
    return redirect("/settings")