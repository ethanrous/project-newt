import datetime
import os
import random
import string

import dotenv
import pymongo
import requests

dotenv.load_dotenv()


# Schema:
"""     {                                    """
"""         "user":{                         """
"""             "id": "",                    """
"""             "name": "",                  """
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
        mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mongoNewt = mongoClient["newtdb"]

        self.userscol = self.mongoNewt["users"]
        self.fridgescol = self.mongoNewt["fridges"]
        self.ingredientscol = self.mongoNewt["ingredients"]

    ##############################
    ### HIGHER LEVEL ENDPOINTS ###
    ##############################

    # Try using these before using more specific endpoints #

    def shareFridgeWithUser(self, userID, fridgeID):
        self.__addFridgeToUser(userID=userID, fridgeID=fridgeID)
        self.__addUserToFridge(userID=userID, fridgeID=fridgeID)

    #############
    ### USERS ###
    #############

    def newUser(self, userID, userName):
        newUserData = {"_id": userID, "name": userName, "fridges": []}
        self.userscol.insert_one(newUserData)
        

    def userExists(self, userID):
        return self.userscol.count_documents({"_id":userID}) > 0


    def __addFridgeToUser(self, userID, fridgeID):
        self.userscol.update_one(
            { "_id": userID },
            { "$push": { "fridges": fridgeID } }
        )

    def getFridgesByUserID(self, userID):
        fridges = self.userscol.find( { "_id": userID }, { "fridges": 1 } )
        return fridges[0]['fridges']

    # CAUTION - THIS DELETES ALL USERS IN THE DATABASE
    def dropUsers(self):
        self.userscol.drop()
        self.userscol = self.mongoNewt["users"]

    ###############
    ### FRIDGES ###
    ###############

    def newFridge(self, ownerID, fridgeName):
        fridgeID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        newFridgeData = {"_id": fridgeID, "ownerID": ownerID, "fridgeName": fridgeName, "collaborators": [], "ingredients": [] }
        self.fridgescol.insert_one(newFridgeData)
        self.__addFridgeToUser(ownerID, fridgeID)
        return

    def getFridge(self, fridgeID):
        fridge = self.fridgescol.find_one( { "_id": fridgeID } )
        return fridge

    def __addUserToFridge(self, userID, fridgeID):
        self.fridgescol.update_one(
            {"_id": fridgeID },
            { "$push": { "collaborators": userID } }
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
                "X-RapidAPI-Key": os.getenv('apiKey'),
                "X-RapidAPI-Host": "nutrition-by-api-ninjas.p.rapidapi.com"
            }

            # Get food data from api
            querystring = {"query": ingredientName}

            print(f"Calling food API for {ingredientName}")
            res = requests.request("GET", foodApiUrl, headers=foodApiHeaders, params=querystring).json()

            if res == []:
                print(f"Adding {ingredientName} to aliases for NO-RES")

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
                print(f"Adding {ingredientName} as an alias for existing ingredient {apiIngredientName} into cache")
                self.ingredientscol.update_one(
                    { "name": apiIngredientName },
                    { "$push": { "aliases": ingredientName } }
                )
            else:
                print(f"Adding new ingredient {ingredientName} with name {apiIngredientName} into cache")
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
            print(f"Found {ingredientName} in cache with name {ingredientData['name']}")
            cleanIngredientName = ingredientData['name']
            ingredientData = ingredientData['nutrition']

        return cleanIngredientName, ingredientData

    # CAUTION - THIS DELETES ALL INGREDIENTS IN THE DATABASE
    def dropIngredents(self):
        self.ingredientscol.drop()
        self.ingredientscol = self.mongoNewt["ingredients"]



## TODO ##
# Does user ID own fridge
# Leave shared fridge