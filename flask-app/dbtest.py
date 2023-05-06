import database
import datetime

def main():
    #userEmail = "ethanrousseau99@gmail.com"
    userEmail = "ethrous@bu.edu"

    dbobj = database.newtdb()
    x, y = 1, 2
    print(x)
    #dbobj.dropUsers()
    #dbobj.dropFridges()
    #dbobj.dropIngredents()
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
