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
    name = userContactInfo['name']
    return render_template('settings.html', userName=name)

@views.route("/notifications")
@login_is_required
def notifications():
    allIngridients = dbobj.getAllIngredientsByUserID(userID=session['google_id'])

    return render_template('notifications.html', ingridients=allIngridients)

@views.route("/recipes", methods=['GET'])
@login_is_required
def recipes():
    return render_template('recipes.html')

@views.route("/fridge/", methods=['GET'])
@login_is_required
def fridge():
    fid = request.args.get('fid')

    if not dbobj.canUserAccessFridge(fid, session['google_id']) or fridge == None:
        return render_template('404.html'), 404

    session["currFridge"] = fid
    collaboratorsContactInfo = list(filter(lambda item: item is not None, [dbobj.getUserContactByUserID(c) for c in dbobj.getFridgeCollaborators(fridgeID=fid)]))

    ingridients = dbobj.getIngredientsInFridge(fridgeID=fid)
    for ingridient in ingridients:
        ingridient['nutrition'] = dbobj.getIngredientDataFromName(ingredientName=ingridient['ingredientName'])

    return render_template('fridge.html', ingridients=ingridients, fridge=dbobj.getFridgeData(fridgeID=fid), collaborators=collaboratorsContactInfo, isOwner=dbobj.doesUserOwnFridge(fid, session['google_id']))


@views.route("/add-ingridient", methods=['POST', 'GET'])
@login_is_required
def add_ingridient():
    itemName, quatityVal, quantityType, expDate, location = request.args.get("item"), request.args.get("quantityValue"), request.args.get("quantityType"), request.args.get("expiration-date"), request.args.get("location")

    fid = session["currFridge"]
    dbobj.addIngredientToFridge(fridgeID=fid, ingredientName=itemName, ingredientExpirationDate=expDate, ingredientQuatity=quatityVal, quantityUnits=quantityType, location=location)

    return redirect(f"/fridge/?fid={fid}")

@views.route("/share-fridge", methods=['POST'])
@login_is_required
def share_fridge():
    collaboratorEmail = request.form.get("share-email")
    collaboratorID = dbobj.getUserIDFromEmail(collaboratorEmail)
    fid = session["currFridge"]

    if dbobj.doesUserExist(collaboratorID) and collaboratorID not in dbobj.getFridgeCollaborators(fid) and collaboratorID != session['google_id']:
        dbobj.shareFridgeWithUser(collaboratorID, fid)

    return redirect(f"/fridge/?fid={fid}")


@views.route("/unshare-fridge/", methods=['GET','POST'])
@login_is_required
def unshare_fridge():

    collabEmail = request.args.get("collabEmail")
    if collabEmail != session['email']:
        collabID = dbobj.getUserIDFromEmail(collabEmail)
        fid = session["currFridge"]
        dbobj.unshareFridgeWithUser(userID=collabID, fridgeID=fid)


    return redirect(f"/fridge/?fid={fid}")


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
    dbobj.removeIngredientFromFridge(fridgeID=fid, ingredientID=int(ingID))
    return redirect(f"/fridge/?fid={fid}")


@views.route("/update-ingredient/", methods=['GET','POST'])
@login_is_required
def update_ingredient():
    fid = session['currFridge']
    ingID = int(request.args.get('ingID'))
    quatityVal = int(request.form.get("quantVal-"+str(ingID)))
    quantityType = request.form.get("quantType-"+str(ingID))

    dbobj.updateIngredient(fridgeID=fid, ingredientID=ingID, newQuantity=quatityVal, newUnits=quantityType)

    return redirect(f"/fridge/?fid={fid}")

