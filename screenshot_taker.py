import database
from artifacts.screenshot_artifact import NewScreenshot
from pymongo import MongoClient
import gridfs
from database import DatabaseService

'''/*
Purpose:The purpose of this method is to take a screenshot of the current screen that is visible to the user as well as to annotate it with its respective metadata
Author: Jose Rodriguez 
Pre-Condition:@requires AVERT to be working.
              @requires AVERT to be connected to the database.

Post-Condition:@ensures the image is saved in png format
               @ensures image has all metadata 

*/'''
def take_screenshot():
    screenshot = NewScreenshot()

    client = MongoClient(port=27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)
    database = DatabaseService(client, db, fs)

    database.screenshot_db_write(
        screenshot.screenshot_file,
        screenshot.screenshot_size,
        screenshot.screenshot_format,
        screenshot.time_stamp,
        screenshot.user_profile.__dict__,
        screenshot.tags,
        screenshot.annotations
    )

    print('Wrote a new screenshot!')
