from pymongo import MongoClient
import database
import gridfs


def get_all_ip_addresses(): #Gets all saved IP addresses from the database
    """
        purpose: gets all saved IP addresses from the database

        @requires AVERT to be connected to the database
        @requires IP addresses to exist within database

        @ensures /result list of all IP addresses obtained from database
    """
    client = MongoClient(port=27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)

    avert_db = database.DatabaseService(client, db, fs)

    return list(set(avert_db.get_all_ips()))
