from pymongo import MongoClient
import database
import gridfs
import artifacts.meta_data_helper
from bson import json_util, ObjectId
import json
from artifacts.meta_data_helper import MetaDataHelper
from artifacts.user_profile_artifact import UserProfileArtifact

'''
Author: Team 3
Purpose: This method will gather all tags and return them in a list
Pre-condition:  @requires AVERT to be connected to the database.
                @requires tags to exist in the database.

Post-condition: @ensures \result a list of all the tags from the database.
'''
def get_all_tags():
    client = MongoClient(port=27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)

    avert_db = database.DatabaseService(client, db, fs)

    return list(set(avert_db.get_all_tags()))

'''
Author: Team 3
Purpose: Takes in a dictionary of tags and deletes them from the database.
Pre-condition:  @requires AVERT to be connected to the database.
                @requires tags to exist in the database.
Post-condition: @ensures \result all tags that were found to be deleted.
'''
def delete_tags(dict):
    client = MongoClient(port=27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)
    dbs = database.DatabaseService(client, db, fs)
    dbs.tags_db_delete(dict.get("artifact_id"), dict.get("tags"))

'''
Author: Team 3
Purpose: Creates a new tag to be placed in the database.
Pre-condition:  @requires AVERT to be connected to the database.
                @requires tag information to be sent to the method when called.
Post-condition: @ensures \result new tag is written inside the database and returns tag information.
'''
def new_tag(dict):
    client = MongoClient(port=27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)
    dbs = database.DatabaseService(client, db, fs)

    user_profile = UserProfileArtifact().__dict__
    
    tag = {
        'label': dict.get("text"),
        'user_profile': user_profile
    }

    tag_return = {
          "ip_address": user_profile.get("ip_address"),
          "mac_address": user_profile.get("mac_address"),
          "description": dict.get("text")
    }
    
    dbs.tags_db_write(dict.get("artifact_id"), tag)
    return tag_return
