from pymongo import MongoClient
import database
import gridfs
import datetime
import base64
from pprint import pprint

DUMMY_IP_ADDRESS = '1.1.1.1.1'
DUMMY_MAC_ADDRESS = '21:43:41:2a:42'
DUMMY_TIMESTAMP = "Some zulu timestamp"


DUMMY_USER_PROFILE = {
    'ip_address': DUMMY_IP_ADDRESS,
    'mac_address': DUMMY_MAC_ADDRESS,
}


DUMMY_TAG = {
    'label': "P0",
    'user_profile': DUMMY_USER_PROFILE
}

DUMMY_ANNOTATION = {
    'timestamp': DUMMY_TIMESTAMP,
    'description': 'This is a nice artifact!',
    'user_profile': DUMMY_USER_PROFILE,
}

DUMMY_ARTIFACT = {
    'user_profile':  DUMMY_USER_PROFILE,
    'timestamp': DUMMY_TIMESTAMP,
    'tags': [DUMMY_TAG],
    'annotations': [DUMMY_ANNOTATION]
}


DUMMY_KEYSTROKE = {
    'artifact': DUMMY_ARTIFACT,
    'key_press': "a",
    "type": 'keystroke'
}


DUMMY_MOUSE_ACTION = {
    '_id': "615c139a72814b71c108a0a8",
    'artifact': DUMMY_ARTIFACT,
    'button': 'left',
    'mouse_action': 'click',
    'mouse_action_value': 'bitmap_area',
    'active_window': 'wireshark',
    'window_focus': 'name_of_focused_application',
    'process': 'wireshark',
    "type": 'mouse_action'

}

"""
Author: Team 3
Purpose: Convert objects that cannot be passed on into the GUI into a JSON-friendly format.
@requires AVERT to be connected to the database.
@ensures \result List with selected artifacts with their respective attributes and metadata.
"""
def sanitize_object_list(result, fs): #Converts objects that can't be passed on into the GUI into a JSON-friendly format
    list_artifacts = []

    for i in range(len(result)): #Converts datetime objects back into normal strings 
        obj = result[i]
        if(obj.get("type") == "screenshot"): #Checks if object is a screenshot artifact
            image_id = obj.get("screenshot_file")
            image = base64.b64encode(fs.get(image_id).read()) #Gets image data from DB and encodes it into base64
            obj["screenshot_file"] = image.decode() #Base 64 is turned into a string and replaces the objectID

        obj["_id"] = str(obj.get("_id")) #Converts ObjectID to string 
        artifact = obj.get("artifact")
        date = artifact.get("timestamp")
        date_str = date.strftime("%H:%M:%ST%Y-%m-%d") #Converts datatime object to string 

        annotation = artifact.get("annotations")
        for j in range(len(annotation)):            #Also in the timestamps in annotations
            annotation_timestamp = annotation[j].get("timestamp")
            annotation_date_str = annotation_timestamp.strftime("%H:%M:%ST%Y-%m-%d")
            artifact["annotations"][j]["timestamp"] = annotation_date_str

        artifact["timestamp"] = date_str
        list_artifacts.append(obj)
    return list_artifacts
    
"""
Author: Team 3
Purpose: Gets the ID of the artifact
@requires AVERT to be connected to the database.
@requires Existing artifact
@requires Artifact ID
@ensures \result Specific artifact by ID
"""
def get_artifact(id):
    client = MongoClient(port = 27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)
    dbs = database.DatabaseService(client, db, fs)
    result = dbs.database_query_id(id)
    selected_artifact = sanitize_object_list([result], fs)
    object = selected_artifact[0]

    pprint(object)
    return object

