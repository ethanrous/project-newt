import database
import datetime

def main():
    userID = 999
    userName = "Ethan"
    userEmail = "ethan@email.com"
    dbobj = database.newtdb()

    dbobj.dropUsers()
    dbobj.dropFridges()
    dbobj.newUser(userID, userName, userEmail)
    dbobj.newUser(1, "Bob", "bob@boberson.com")
    print(f"User ID: {dbobj.getUserIDFromEmail(userEmail)}")
    print(f"No User ID: {dbobj.getUserIDFromEmail('dude@dood.com')}")

    dbobj.newFridge(ownerID=userID, fridgeName="Ethan's Fridge")

    dbobj.newFridge(ownerID=1, fridgeName="Other Fridge")

    fridges = dbobj.getFridgesByUserID(userID=userID)
    otherFridges = dbobj.getFridgesByUserID(userID=1)
    print(f"Does user own fridge? {dbobj.doesUserOwnFridge(fridges[0], userID)}")
    print(f"Does user own fridge? {dbobj.doesUserOwnFridge(otherFridges[0], 999)}")

    print(f"Can user access fridge? {dbobj.canUserAccessFridge(fridges[0], 1)}")
    print("Add user to fridge")
    dbobj.shareFridgeWithUser(1, fridges[0])
    print(f"Can user access fridge? {dbobj.canUserAccessFridge(fridges[0], 1)}")
    print("Remove user from fridge")
    dbobj.unshareFridgeWithUser(1, fridges[0])
    print(f"Can user access fridge? {dbobj.canUserAccessFridge(fridges[0], 1)}")

    dbobj.addIngredientToFridge(fridgeID=fridges[0], ingredientName="Apple", ingredientExpirationDate=datetime.date.today().strftime("%Y-%m-%d"), ingredientQuatity=1, quantityUnits="Count")

    ingredients = dbobj.getIngredientsInFridge(fridgeID=fridges[0])
    dbobj.removeIngredientFromFridge(fridges[0], ingredientID=ingredients[0]['ingredientID'])

    #dbobj.dropIngredents()
    data = dbobj.getIngredientDataFromName("Apple")
    data = dbobj.getIngredientDataFromName("Bapple")
main()
