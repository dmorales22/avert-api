import artifacts.meta_data_helper
from pymongo import MongoClient
import database
import gridfs
import datetime
from bson import json_util, ObjectId
import json
from artifacts.meta_data_helper import MetaDataHelper
from artifacts.user_profile_artifact import UserProfileArtifact

"""
Author: Team 3
Purpose: Writes an annotation gotten fmro the GUI to an specific document in the database
@requires AVERT to be connected to the database.
@requires Existing dictionary
@ensures \result Annotation gets logged in the database with its respective information.
"""
def annotate(dict):
    client = MongoClient(port=27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)
    dbs = database.DatabaseService(client, db, fs)
    user_profile = UserProfileArtifact().__dict__
    timestamp = MetaDataHelper.get_zulu_time()

    annotation = {
        'timestamp': timestamp,
        'description': dict.get("text"),
        'user_profile': user_profile
    }

    print('ATTEMPTING TO WRITE ANNOTATION')
    dbs.annotation_db_write(dict.get("artifact_id"), annotation)
    print('FINISHED WRITE ANNOTATION')

    annotation_return = {
        "timestamp": timestamp,
        "ip_address": user_profile.get("ip_address"),
        "mac_address": user_profile.get("mac_address"),
        "description": dict.get("text")
    }
    return annotation_return
