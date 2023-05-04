import database
import datetime

def main():
    # userID = 999
    # userName = "Ethan"
    dbobj = database.newtdb()

    # dbobj.dropUsers()
    # dbobj.dropFridges()
    # dbobj.newUser(userID, userName)
    # dbobj.newFridge(ownerID=userID, fridgeName="Ethan's Fridge2")
    # dbobj.newFridge(ownerID=userID, fridgeName="Ethan's Fridge1")
    # dbobj.newFridge(ownerID=userID, fridgeName="Ethan's Fridge0")

    # fridges = dbobj.getFridgesByUserID(userID=userID)
    # #print("Fridges: ", fridges)
    # #print("First fridge: ", dbobj.getFridge(fridgeID=fridges[1]))

    # check = dbobj.userExists(userID=userID)
    # #print("Does the user exists? ", check)

    # dbobj.addIngredientToFridge(fridgeID=fridges[0], ingredientName="Apple", ingredientExpirationDate=datetime.date.today().strftime("%Y-%m-%d"), ingredientQuatity=1, quantityUnits="Count", location="fridge")

    # ingredients = dbobj.getIngredientsInFridge(fridgeID=fridges[0])
    # #print("Ingridients: ", ingredients)
    # dbobj.removeIngredientFromFridge(fridges[0], ingredientID=ingredients[0]['ingredientID'])

    
    # data = dbobj.getIngredientDataFromName("Apple")
    # #data = dbobj.getIngredientDataFromName("Bapple")
    # print(type(data))
    dbobj.dropIngredents()
    dbobj.dropFridges()
    dbobj.dropUsers()
main()
