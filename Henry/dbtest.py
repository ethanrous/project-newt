import database
import datetime

def main():
    userID = 999
    userName = "Ethan"
    dbobj = database.newtdb()

    dbobj.dropUsers()
    dbobj.dropFridges()
    dbobj.newUser(userID, userName)
    dbobj.newFridge(ownerID=userID, fridgeName="Ethan's Fridge2")

    fridges = dbobj.getFridgesByUserID(userID=userID)

    dbobj.addIngredientToFridge(fridgeID=fridges[0], ingredientName="Apple", ingredientExpirationDate=datetime.date.today().strftime("%Y-%m-%d"), ingredientQuatity=1, quantityUnits="Count")

    ingredients = dbobj.getIngredientsInFridge(fridgeID=fridges[0])
    dbobj.removeIngredientFromFridge(fridges[0], ingredientID=ingredients[0]['ingredientID'])

    data = dbobj.getIngredientDataFromName("Apple")
    data = dbobj.getIngredientDataFromName("Bapple")
main()
