import datetime
import os
import random
import string

import pymongo
from bson.objectid import ObjectId
import requests

# Schema:
"""     {                                    """
"""         "user":{                         """
"""             "id": "",                    """
"""             "name": "",                  """
"""             "email": "",                 """
"""             "ownedFridges": ["ids"]      """
"""             "sharedFridges": ["ids"]     """
"""         },                               """
"""         "fridge":{                       """
"""             "id": "",                    """
"""             "owner_id": "",              """
"""             "collaborators":["ids"],     """
"""             "ingridients": ["ids"]       """
"""         },                               """
"""         "ingridients": {                 """
"""             "id": 0,                     """
"""             "name": "",                  """
"""             "expiration_date": "",       """
"""             "dateAdded": "",             """
"""             "quatity": ""                """
"""             "location": ""               """
"""         }                                """
"""         "nutritionCache": {              """
"""             "name":"",                   """
"""             "aliases": [""],             """
"""             "nutrition": {}              """
"""         }                                """
"""     }                                    """
"""                                          """

class newtdb:
    pass

    def __init__(self):
        mongoURL = os.getenv('MONGO_URL') # ex. mongodb://localhost:27017/
        mongoClient = pymongo.MongoClient(mongoURL)

        self.mongoNewt = mongoClient["newtdb"]

        self.userscol = self.mongoNewt["users"]
        self.fridgescol = self.mongoNewt["fridges"]
        self.ingredientscol = self.mongoNewt["ingredients"]
        self.nutritioncol = self.mongoNewt["nutritionCache"]

        self.nutritionApiKey = os.getenv('NUTRITION_API_KEY')

    ##############################
    ### HIGHER LEVEL ENDPOINTS ###
    ##############################

    # Try using these before using more specific endpoints #

    def shareFridgeWithUser(self, userID, fridgeID):
        self.addSharedFridgeToUser(userID=userID, fridgeID=fridgeID)
        self.addUserToFridge(userID=userID, fridgeID=fridgeID)

    def unshareFridgeWithUser(self, userID, fridgeID):
        self.removeSharedFridgeFromUser(userID=userID, fridgeID=fridgeID)
        self.removeUserFromFridge(userID=userID, fridgeID=fridgeID)

    #############
    ### USERS ###
    #############

    def newUser(self, userID, userName, email):
        newUserData = {"_id": userID, "name": userName, "email": email, "ownedFridges": [], "sharedFridges": []}
        self.userscol.insert_one(newUserData)

    def doesUserExist(self, userID):
        if self.userscol.find_one( { "_id": userID } ):
            return True
        return False

    def getUserContactByUserID(self, userID):
        contactInfo = self.userscol.find_one({ "_id": userID }, { "_id": 0, "name": 1, "email": 1})
        return contactInfo

    def addOwnedFridgeToUser(self, userID, fridgeID):
        self.userscol.update_one(
            { "_id": userID },
            { "$push": { "ownedFridges": fridgeID } }
        )

    def addSharedFridgeToUser(self, userID, fridgeID):
        self.userscol.update_one(
            { "_id": userID },
            { "$push": { "sharedFridges": fridgeID } }
        )

    def removeOwnedFridgeFromUser(self, userID, fridgeID):
        self.userscol.update_one(
            { "_id": userID },
            { "$pull": { "ownedFridges": fridgeID } }
        )

    def removeSharedFridgeFromUser(self, userID, fridgeID):
        self.userscol.update_one(
            { "_id": userID },
            { "$pull": { "sharedFridges": fridgeID } }
        )

    def getOwnedFridgesByUserID(self, userID):
        fridges = list(self.userscol.find( { "_id": userID }, { "_id": 0, "ownedFridges": 1 } ) )
        if fridges != [] and fridges != [{}]:
            return fridges[0]['ownedFridges']
        return []

    def getCollabFridgesByUserID(self, userID):
        fridges = list(self.userscol.find( { "_id": userID }, { "_id": 0, "sharedFridges": 1 } ) )
        if fridges != [] and fridges != [{}]:
            return fridges[0]['sharedFridges']
        else:
            return []

    def getUserIDFromEmail(self, email):
        uid = self.userscol.find_one( { "email": email }, { "_id": 1 } )
        if uid != None:
            uid = uid['_id']
        return uid

    def getUserContactByUserID(self, userID):
        return self.userscol.find_one( { "_id": userID }, { "_id": 0, "name": 1, "email": 1} )

    def updateUserName(self, userID, newName):
        self.userscol.update_one( {"_id": userID }, { "$set": { "name": newName } } )

    def getFridgesByUserID(self, userID):
        collabs = self.getCollabFridgesByUserID(userID=userID)
        owned = self.getOwnedFridgesByUserID(userID=userID)
        fridges = collabs + owned
        return fridges

    # CAUTION - THIS DELETES ALL USERS IN THE DATABASE
    def dropUsers(self):
        self.userscol.drop()
        self.userscol = self.mongoNewt["users"]

    ###############
    ### FRIDGES ###
    ###############

    def newFridge(self, ownerID, fridgeName):
        if not self.doesUserExist(ownerID):
            raise(Exception(f"Attempting to create fridge with non-existant userID: {ownerID}"))

        fridgeID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        newFridgeData = {"_id": fridgeID, "ownerID": ownerID, "fridgeName": fridgeName, "collaborators": [], "ingredients": [] }
        self.fridgescol.insert_one(newFridgeData)
        self.addOwnedFridgeToUser(ownerID, fridgeID)

    def getFridgeData(self, fridgeID):
        fridge = self.fridgescol.find_one( { "_id": fridgeID } )
        return fridge

    def addUserToFridge(self, userID, fridgeID):
        self.fridgescol.update_one(
            {"_id": fridgeID },
            { "$push": { "collaborators": userID } }
        )

    def removeUserFromFridge(self, userID, fridgeID):
        self.fridgescol.update_one(
            {"_id": fridgeID },
            { "$pull": { "collaborators": userID } }
        )

    def addIngredientToFridge(self, fridgeID, newIngredientID):
        self.fridgescol.update_one(
            { "_id": fridgeID },
            { "$push": { "ingredients": newIngredientID } }
        )

    def updateIngredient(self, ingredientID, newQuantity, newUnits):
        self.fridgescol.update_one(
            { "_id": ingredientID },
            { "$set": { "quatity": newQuantity } },
            { "$set": { "quatityUnits": newUnits } }
        )

    def removeIngredientFromFridge(self, fridgeID, ingredientID):
        self.fridgescol.update_one(
            { "_id": fridgeID },
            { "$pull": { "ingredients": ingredientID } }
        )

    def getIngredientsInFridge(self, fridgeID):
        ingredientIDs = self.fridgescol.find_one( { "_id": fridgeID }, { "_id": 0, "ingredients": 1 } )['ingredients']
        ingredientIDs = list(map(lambda x : ObjectId(x), ingredientIDs))

        ingData = list(self.ingredientscol.find( {"_id": { "$in": ingredientIDs } } ) )

        for ing in ingData:
            ing["_id"] = str(ing["_id"])

        return ingData

    def doesUserOwnFridge(self, fridgeID, userID):
        fridgeOwner = self.fridgescol.find_one( { "_id": fridgeID }, { "ownerID": 1 } )
        return fridgeOwner and fridgeOwner['ownerID'] == userID

    def canUserAccessFridge(self, fridgeID, userID):
        return self.doesUserOwnFridge(fridgeID, userID) or self.fridgescol.find_one( { "_id": fridgeID, "collaborators": userID } )

    def getFridgeCollaborators(self, fridgeID):
        return (self.fridgescol.find_one( { "_id": fridgeID }, {"_id": 0, "collaborators": 1} ))['collaborators']

    def deleteFridge(self, fridgeID, userID):
        if not self.doesUserOwnFridge(fridgeID, userID):
            return

        self.removeOwnedFridgeFromUser(userID=userID, fridgeID=fridgeID)

        for user in self.getFridgeCollaborators(fridgeID):
            self.removeSharedFridgeFromUser(user, fridgeID)

        self.userscol.delete_one({ "_id": fridgeID })


    # CAUTION - THIS DELETES ALL FRIDGES IN THE DATABASE
    def dropFridges(self):
        self.fridgescol.drop()
        self.fridgescol = self.mongoNewt["fridges"]


    ###################
    ### INGREDIENTS ###
    ###################

    def newIngredient(self, name, expirationDate, quatity, quantityUnits, location):
        newIngredientData = {
            "name": name,
            "expirationDate": expirationDate,
            "dateAdded": datetime.date.today().strftime("%Y-%m-%d"),
            "quatity": quatity,
            "quantityUnits": quantityUnits, # Count, lbs, gallons, etc.
            "location": location
        }
        return str(self.ingredientscol.insert_one(newIngredientData).inserted_id)

    # CAUTION - THIS DELETES ALL INGREDIENTS IN THE DATABASE
    def dropIngredients(self):
        self.ingredientscol.drop()
        self.ingredientscol = self.mongoNewt["ingredients"]


    #######################
    ### NUTRITION CACHE ###
    #######################

    def getIngredientDataFromName(self, ingredientName):

        ingredientData = self.nutritioncol.find_one( { "aliases": ingredientName } )

        if ingredientData == None:

            foodApiUrl = "https://nutrition-by-api-ninjas.p.rapidapi.com/v1/nutrition"
            foodApiHeaders = {
                "X-RapidAPI-Key": self.nutritionApiKey,
                "X-RapidAPI-Host": "nutrition-by-api-ninjas.p.rapidapi.com"
            }

            # Get food data from api
            querystring = {"query": ingredientName}

            res = requests.request("GET", foodApiUrl, headers=foodApiHeaders, params=querystring).json()

            if res == []:
                if not self.nutritioncol.find_one( { "name": "NO-RES" } ):
                    newIngredientData = {
                        "name": "NO-RES",
                        "aliases": [],
                        "nutrition": None
                    }
                    self.nutritioncol.insert_one(newIngredientData)

                self.nutritioncol.update_one(
                    { "name": "NO-RES" },
                    { "$push": { "aliases": ingredientName } }
                )
                return None, None

            apiIngredientData = res[0]
            apiIngredientName = apiIngredientData['name']

            del apiIngredientData['name']

            if self.nutritioncol.find_one( { "name": apiIngredientName } ):
                self.nutritioncol.update_one(
                    { "name": apiIngredientName },
                    { "$push": { "aliases": ingredientName } }
                )
            else:
                newIngredientData = {
                    "name": apiIngredientName,
                    "aliases": [ingredientName],
                    "nutrition": apiIngredientData
                }
                self.nutritioncol.insert_one(newIngredientData)
            ingredientData = apiIngredientData
            cleanIngredientName = apiIngredientName

        elif ingredientData['name'] == "NO_RES":
            cleanIngredientName = None
            ingredientData = []

        else:
            cleanIngredientName = ingredientData['name']
            ingredientData = ingredientData['nutrition']

        return cleanIngredientName, ingredientData

    # CAUTION - THIS DELETES ALL NUTRITION CACHE DATA IN THE DATABASE
    def dropNutritionCache(self):
        self.nutritioncol.drop()
        self.nutritioncol = self.mongoNewt["nutritionCache"]

