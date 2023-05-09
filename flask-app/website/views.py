import time

from itertools import chain

from flask import (Blueprint, Flask, abort, flash, redirect, render_template,
                   request, session, url_for)
from flask_login import current_user, login_required

from . import dbobj

views = Blueprint("views", __name__)

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        elif not dbobj.doesUserExist(session['google_id']):
            return redirect('/')
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
    return render_template('home.html', ownedFridges=ownedFridges, sharedFridges=sharedFridges, totalExpired=dbobj.getTotalExpired(session['google_id']))

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
    name = userContactInfo['name']
    return render_template('settings.html', userName=name, totalExpired=dbobj.getTotalExpired(session['google_id']))

@views.route("/notifications")
@login_is_required
def notifications():
    session['url'] = "/notifications"

    allingredients = dbobj.getAllIngredientsByUserID(userID=session['google_id'])

    count = 0
    for count, ingedient in enumerate(allingredients):
        if not dbobj.isExpired(ingedient['expirationDate']):
            break
    else:
        if count == 0:
            count = 1

    expiredIngredients = allingredients[:count]
    goodIngredients = allingredients[count:]

    return render_template('notifications.html', expiredIngredients=expiredIngredients, goodIngredients=goodIngredients, totalExpired=dbobj.getTotalExpired(session['google_id']))

@views.route("/recipes", methods=['GET'])
@login_is_required
def recipes():
    return render_template('recipes.html', totalExpired=dbobj.getTotalExpired(session['google_id']))

@views.route("/fridge/", methods=['GET'])
@login_is_required
def fridge():
    fid = request.args.get('fid')

    session['url'] = f"/fridge/?fid={fid}"

    if not dbobj.canUserAccessFridge(fid, session['google_id']) or fridge == None:
        return render_template('404.html'), 404

    session["currFridge"] = fid
    collaboratorsContactInfo = list(filter(lambda item: item is not None, [dbobj.getUserContactByUserID(c) for c in dbobj.getFridgeCollaborators(fridgeID=fid)]))

    ingredients = dbobj.getIngredientsInFridge(fridgeID=fid)

    for ingredient in ingredients:
        ingredient['nutrition'] = dbobj.getIngredientDataFromID(ingredientID=ingredient['nutritionID'])['nutrition']

    return render_template('fridge.html', ingredients=ingredients, fridge=dbobj.getFridgeData(fridgeID=fid), collaborators=collaboratorsContactInfo, isOwner=dbobj.doesUserOwnFridge(fid, session['google_id']), totalExpired=dbobj.getTotalExpired(session['google_id']))

@views.route("/add-ingredient", methods=['POST', 'GET'])
@login_is_required
def add_ingredient():
    itemName, quatityVal, quantityType, expDate, location = request.args.get("item"), request.args.get("quantityValue"), request.args.get("quantityType"), request.args.get("expiration-date"), request.args.get("location")

    fid = session["currFridge"]
    newIngredientID = dbobj.newIngredient(fid, itemName, expDate, quatityVal, quantityType, location)
    dbobj.addIngredientToFridge(fridgeID=fid, newIngredientID=newIngredientID)

    return redirect(session['url'])

@views.route("/share-fridge", methods=['POST'])
@login_is_required
def share_fridge():
    collaboratorEmail = request.form.get("share-email")
    collaboratorID = dbobj.getUserIDFromEmail(collaboratorEmail)
    fid = session["currFridge"]

    if dbobj.doesUserExist(collaboratorID) and collaboratorID not in dbobj.getFridgeCollaborators(fid) and collaboratorID != session['google_id']:
        dbobj.shareFridgeWithUser(collaboratorID, fid)

    return redirect(session['url'])

@views.route("/unshare-fridge/", methods=['GET','POST'])
@login_is_required
def unshare_fridge():

    collabEmail = request.args.get("collabEmail")
    if collabEmail != session['email']:
        collabID = dbobj.getUserIDFromEmail(collabEmail)
        fid = session["currFridge"]
        dbobj.unshareFridgeWithUser(userID=collabID, fridgeID=fid)


    return redirect(session['url'])

@views.route("/delete-fridge", methods=['GET','POST'])
@login_is_required
def delete_fridge():
    fid = session['currFridge']
    dbobj.deleteFridge(fid, session['google_id'])
    return redirect("/home")

@views.route("/change-name", methods=['GET','POST'])
@login_is_required
def change_name():
    name = request.form.get('name')
    dbobj.updateUserName(userID=session['google_id'],newName=name)
    session['name'] = name
    return redirect("/settings")

@views.route("/delete-ingredient/", methods=['GET','POST'])
@login_is_required
def delete_ingredient():
    fid = session['currFridge']
    ingID = request.args.get('ingID')
    dbobj.removeIngredientFromFridge(fridgeID=fid, ingredientID=ingID)
    return redirect(session['url'])

@views.route("/update-ingredient/", methods=['GET','POST'])
@login_is_required
def update_ingredient():
    ingID = request.args.get('ingID')
    quatityVal = int(request.form.get("quantVal-"+str(ingID)))
    quantityType = request.form.get("quantType-"+str(ingID))

    dbobj.updateIngredient(ingredientID=ingID, newQuantity=quatityVal, newUnits=quantityType)

    return redirect(session['url'])

