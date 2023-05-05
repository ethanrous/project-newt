import datetime
import os
import random
import string

import pymongo
import requests

# Schema:
"""     {                                    """
"""         "user":{                         """
"""             "id": "",                    """
"""             "name": "",                  """
"""             "email": "",                 """
"""             "fridges": ["ids"]           """
"""         },                               """
"""         "fridge":{                       """
"""             "id": "",                    """
"""             "owner_id": "",              """
"""             "collaborators":["ids"],     """
"""             "ingridients": [{            """
"""                 "id": 0,                 """
"""                 "name": "",              """
"""                 "expiration_date": "",   """
"""                 "dateAdded": "",         """
"""                 "quatity": ""            """
"""                 "location": ""           """
"""             }]                           """
"""         },                               """
"""         "ingridients": {                 """
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

        self.nutritionApiKey = os.getenv('NUTRITION_API_KEY')

    ##############################
    ### HIGHER LEVEL ENDPOINTS ###
    ##############################

    # Try using these before using more specific endpoints #

    def shareFridgeWithUser(self, userID, fridgeID):
        self.__addFridgeToUser(userID=userID, fridgeID=fridgeID)
        self.__addUserToFridge(userID=userID, fridgeID=fridgeID)

    def unshareFridgeWithUser(self, userID, fridgeID):
        self.__removeFridgeFromUser(userID=userID, fridgeID=fridgeID)
        self.__removeUserFromFridge(userID=userID, fridgeID=fridgeID)

    #############
    ### USERS ###
    #############

    def newUser(self, userID, userName, email):
        newUserData = {"_id": userID, "name": userName, "email": email, "fridges": []}
        self.userscol.insert_one(newUserData)

    def doesUserExist(self, userID):
        if self.userscol.find_one( { "_id": userID } ):
            return True
        return False

    def getUserContactByUserID(self, userID):
        contactInfo = self.userscol.find_one({ "_id": userID }, { "_id": 0, "name": 1, "email": 1})
        return contactInfo

    def __addFridgeToUser(self, userID, fridgeID):
        self.userscol.update_one(
            { "_id": userID },
            { "$push": { "fridges": fridgeID } }
        )

    def __removeFridgeFromUser(self, userID, fridgeID):
        self.userscol.update_one(
            { "_id": userID },
            { "$pull": { "fridges": fridgeID } }
        )

    def getFridgesByUserID(self, userID):
        fridges = self.userscol.find( { "_id": userID }, { "fridges": 1 } )
        return fridges[0]['fridges']

    def getUserIDFromEmail(self, email):
        uid = self.userscol.find_one( { "email": email }, { "_id": 1 } )
        if uid != None:
            uid = uid['_id']
        return uid

    def getUserContactByUserID(self, userID):
        return self.userscol.find_one({ "_id": userID }, { "_id": 0, "name": 1, "email": 1} )

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
        self.__addFridgeToUser(ownerID, fridgeID)


    def getFridgeData(self, fridgeID):
        fridge = self.fridgescol.find_one( { "_id": fridgeID } )
        return fridge

    def __addUserToFridge(self, userID, fridgeID):
        self.fridgescol.update_one(
            {"_id": fridgeID },
            { "$push": { "collaborators": userID } }
        )

    def __removeUserFromFridge(self, userID, fridgeID):
        self.fridgescol.update_one(
            {"_id": fridgeID },
            { "$pull": { "collaborators": userID } }
        )

    def addIngredientToFridge(self, fridgeID, ingredientName, ingredientExpirationDate, ingredientQuatity, quantityUnits, location):
        while True:
            newIngredientID = random.randint(1, 1000)
            possibleCollision = self.fridgescol.aggregate( [ {"$match": { "_id": fridgeID, 'ingredients.ingredientID': newIngredientID } }, { "$unwind": { "path": "$ingredients" } } ] )
            if len(list(possibleCollision)) == 0:
                break

        ingredientData = {
            "ingredientID": newIngredientID,
            "ingredientName": ingredientName,
            "ingredientExpirationDate": ingredientExpirationDate,
            "dateAdded": datetime.date.today().strftime("%Y-%m-%d"),
            "ingredientQuatity": ingredientQuatity,
            "quantityUnits": quantityUnits, # Count, lbs, gallons, etc.
            "location": location
        }

        self.fridgescol.update_one(
            { "_id": fridgeID },
            { "$push": { "ingredients": ingredientData } }
        )

    def removeIngredientFromFridge(self, fridgeID, ingredientID):
        self.fridgescol.update_one(
            { "_id": fridgeID },
            { "$pull": { "ingredients": { "ingredientID": ingredientID } } }
        )

    def getIngredientsInFridge(self, fridgeID):
        fridge = self.fridgescol.find_one( { "_id": fridgeID } )
        ingredients = fridge["ingredients"]
        return ingredients

    def doesUserOwnFridge(self, fridgeID, userID):
        fridgeOwner = self.fridgescol.find_one( { "_id": fridgeID }, { "ownerID": 1 } )
        if fridgeOwner and fridgeOwner['ownerID'] == userID:
            return True
        return False

    def canUserAccessFridge(self, fridgeID, userID):
        if self.doesUserOwnFridge(fridgeID, userID) or self.fridgescol.find_one( { "_id": fridgeID, "collaborators": userID } ):
            return True
        return False

    def getFridgeCollaborators(self, fridgeID):
        fridge = self.getFridge(fridgeID)
        collaboratorsID = fridge["collaborators"]
        return collaboratorsID

    def getFridgeCollaborators(self, fridgeID):
        collaborators = self.fridgescol.find_one( { "_id": fridgeID }, {"_id": 0, "collaborators": 1} )
        return collaborators

    # CAUTION - THIS DELETES ALL FRIDGES IN THE DATABASE
    def dropFridges(self):
        self.fridgescol.drop()
        self.fridgescol = self.mongoNewt["fridges"]

    ###################
    ### INGREDIENTS ###
    ###################

    def getIngredientDataFromName(self, ingredientName):

        ingredientData = self.ingredientscol.find_one( { "aliases": ingredientName } )

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
                if not self.ingredientscol.find_one( { "name": "NO-RES" } ):
                    newIngredientData = {
                        "name": "NO-RES",
                        "aliases": [],
                        "nutrition": None
                    }
                    self.ingredientscol.insert_one(newIngredientData)

                self.ingredientscol.update_one(
                    { "name": "NO-RES" },
                    { "$push": { "aliases": ingredientName } }
                )
                return []

            apiIngredientData = res[0]
            apiIngredientName = apiIngredientData['name']

            del apiIngredientData['name']

            if self.ingredientscol.find_one( { "name": apiIngredientName } ):
                self.ingredientscol.update_one(
                    { "name": apiIngredientName },
                    { "$push": { "aliases": ingredientName } }
                )
            else:
                newIngredientData = {
                    "name": apiIngredientName,
                    "aliases": [ingredientName],
                    "nutrition": apiIngredientData
                }
                self.ingredientscol.insert_one(newIngredientData)
            ingredientData = apiIngredientData
            cleanIngredientName = apiIngredientName

        elif ingredientData['name'] == "NO_RES":
            cleanIngredientName = None
            ingredientData = []

        else:
            cleanIngredientName = ingredientData['name']
            ingredientData = ingredientData['nutrition']

        return cleanIngredientName, ingredientData

    # CAUTION - THIS DELETES ALL INGREDIENTS IN THE DATABASE
    def dropIngredents(self):
        self.ingredientscol.drop()
        self.ingredientscol = self.mongoNewt["ingredients"]



## TODO ##
# Get soon to expire ingredients
