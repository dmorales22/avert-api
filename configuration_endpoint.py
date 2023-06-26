from pymongo import MongoClient
import database
import gridfs

def recording_settings():
    client = MongoClient(port = 27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)
    dbs = database.DatabaseService(client, db, fs)

    return dbs.configuration_db_get()

def update_recording_settings(settings):
    client = MongoClient(port = 27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)
    dbs = database.DatabaseService(client, db, fs)
    
    print(settings)
    dbs.configuration_db_write(settings.get("keystrokes"),settings.get("mouse_actions"),settings.get("screenshot"),settings.get("process"),settings.get("window_history"),settings.get("system_call"), settings.get("video"), settings.get("network_activity"))