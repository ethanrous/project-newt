import database
import datetime

def main():
    #userEmail = "ethanrousseau99@gmail.com"
    userEmail = "ethrous@bu.edu"

    dbobj = database.newtdb()

    dbobj.dropUsers()
    dbobj.dropFridges()
    dbobj.dropIngredients()

    dbobj.newIngredient("Apple", "2023-01-01", 1, "Count", "Freezer")
    return
    userID = dbobj.getUserIDFromEmail(userEmail)
    fridges = dbobj.getOwnedFridgesByUserID(userID=userID)
    print(fridges)
    ing = dbobj.getIngredientsInFridge(fridges[0])
    print(ing)
    dbobj.updateIngredient(fridges[0], 158, newQuantity=2, newUnits="Count")
    ing = dbobj.getIngredientsInFridge(fridges[0])
    print(ing)


main()
