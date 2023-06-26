import gridfs
import database
from pymongo import MongoClient



def get_all_mac_addresses():
    """
    Purpose: Gets all saved MAC addresses from the Database

    @requires: AVERT to be connected to the database
    @requires: MAC addresses to exist within database 

    @ensures /result list of all MAC addresses obtained from database.
    """
    client = MongoClient(port=27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)

    avert_db = database.DatabaseService(client, db, fs)

    return list(set(avert_db.get_all_macs()))
