import copy
from pymongo import MongoClient
import database
import gridfs
import datetime
from bson import json_util, ObjectId
import json

DUMMY_SEARCH_RESULT = {
    'id': 0,
    'timestamp': 'Some timestamp',
    'type': 'mouse_action',
    'ip_address': '1.1.1.1.1',
    'mac_address': '1a.2a.41.41.412',
    'description': 'THis is a cool artifact'
}


# pulls attributes from full artifacts into shorten dicts to display in the GUI
def shortened_artifact(object_list):
    list = []
    for i in range(len(object_list)):
        object = object_list[i]
        artifact = object.get("artifact")
        user_profile = artifact.get("user_profile")
        annotation = artifact.get("annotations")

        annotation_description: str = ""

        if object['type'] == 'network_activity':
            annotation_description = object['summary']
        elif annotation:
            annotation_description = annotation[0].get("description")

        test = {  # Creates shortened artifact here
            'id': object.get("_id"),
            'timestamp': artifact.get("timestamp"),
            'type': object.get("type"),
            'ip_address': user_profile.get("ip_address"),
            'mac_address': user_profile.get("mac_address"),
            'description': annotation_description
        }
        list.append(test)
    return list


def sanitize_object_list(result):
    list_artifacts = []

    for i in range(len(result)):  # Converts datetime objects back into normal strings
        obj = result[i]
        obj["_id"] = str(obj.get("_id"))
        artifact = obj.get("artifact")
        date = artifact.get("timestamp")
        date_str = date.strftime("%H:%M:%ST%Y-%m-%d")

        annotation = artifact.get("annotations")
        for j in range(len(annotation)):  # Also in the timestamps in annotations
            annotation_timestamp = annotation[j].get("timestamp")
            annotation_date_str = annotation_timestamp.strftime(
                "%H:%M:%ST%Y-%m-%d")
            artifact["annotations"][j]["timestamp"] = annotation_date_str

        artifact["timestamp"] = date_str
        list_artifacts.append(obj)
    return list_artifacts


def search(query):
    client = MongoClient(port=27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)
    db_obj = database.DatabaseService(client, db, fs)
    result = db_obj.database_query(query)
    list_artifacts = sanitize_object_list(result)
    # Get attributes from full objects
    search = shortened_artifact(list_artifacts)
    return search
