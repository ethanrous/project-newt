import database
import datetime

def main():
    userEmail = "ethanrousseau99@gmail.com"
    dbobj = database.newtdb()
    # userID = dbobj.getUserIDFromEmail(userEmail)
    # print(userID)
    # print(f"Owner: {dbobj.getOwnedFridgesByUserID(userID=userID)}")
    # print(f"Collab: {dbobj.getCollabFridgesByUserID(userID=userID)}")
    dbobj.dropFridges()
    dbobj.dropIngredents()
    dbobj.dropUsers()

main()
