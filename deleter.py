import database
from artifacts.screenshot_artifact import NewScreenshot
from pymongo import MongoClient
import gridfs
from database import DatabaseService

'''
Author: Team 3
Purpose: This method takes in an ID and deletes it from the database.
Pre-condition:@requires to take in an ID to be deleted.
              @requires AVERT to be connected to the database.
              @requires the ID to exist in the database.
Post-condition: @ensures \result that the ID that was sent is deleted.
'''
def delete_ids(ids):
    screenshot = NewScreenshot()

    client = MongoClient(port=27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)
    database = DatabaseService(client, db, fs)

    for _id in ids:
        database.database_delete_id(_id)

    print('Ids deleted!')
