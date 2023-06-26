from pymongo import MongoClient
import database
import gridfs
import os
import requests
import json
from bson import ObjectId
import datetime
import base64
import subprocess
import socket
import shutil

keystroke_total_count = 0
mouse_action_total_count = 0
screenshot_total_count = 0
process_total_count = 0
window_history_total_count = 0
system_call_total_count = 0
video_total_count = 0
network_activity_total_count = 0
artifact_total_count = 0

keystroke_counter = 0
mouse_action_counter = 0
screenshot_counter = 0
process_counter = 0
window_history_counter = 0
system_call_counter = 0
video_counter = 0
network_activity_counter = 0
artifact_counter = 0

keystroke_active = True
mouse_action_active = True
screenshot_active = True
process_active = True
window_history_active = True
system_call_active = True
video_active = True
network_activity_active = True

# Creates video symlink for GUI to use
def video_symlink(video_name, video_file_link):
    if not os.path.isdir('../avert-gui/public/videos/'):  # Checks if dir exists
        # Creates one if it doesn't
        os.mkdir('../avert-gui/public/videos/')

    # Runs command to create symlink to public/videos/ dir
    command = ["ln", "-s", video_file_link, "../avert-gui/public/videos/" + video_name]
    run_command = subprocess.Popen(command, stdout=subprocess.PIPE)

# Desanitizes objects to make it MongoDB friendly
def desanitize_object(obj, fs): #Converts objects that can't be passed on into the GUI into a JSON-friendly format
    if(obj.get("type") == "screenshot"): #Checks if object is a screenshot artifact
        image_base64_str = obj.get("screenshot_file")
        image_base64_bytes = image_base64_str.encode('utf-8')
        image_bytes = base64.b64decode(image_base64_bytes) # Converts from base64 bytes to bytes
        obj["screenshot_file"] = image_bytes # Stores bytes info 

    if(obj.get("type") == "network_activity"): #Checks if object is a network activity artifact
        start_time_str = obj.get("start_time")
        end_time_str = obj.get("end_time")
        start_time_obj = datetime.datetime.strptime(start_time_str, "%H:%M:%ST%Y-%m-%d") #Converts date string into a datetime object
        end_time_obj = datetime.datetime.strptime(end_time_str, "%H:%M:%ST%Y-%m-%d")
        obj["start_time"] = start_time_obj
        obj["end_time"] = end_time_obj

    obj["_id"] = ObjectId(obj.get("_id")) #Converts string to ObjectID 
    artifact = obj.get("artifact")
    date_str = artifact.get("timestamp")
    date_obj = datetime.datetime.strptime(date_str, "%H:%M:%ST%Y-%m-%d") #Converts string to datetime object 

    annotation = artifact.get("annotations")
    for j in range(len(annotation)):            #Also in the timestamps in annotations
        annotation_timestamp_str = annotation[j].get("timestamp")
        annotation_date_object = datetime.datetime.strptime(annotation_timestamp_str, "%H:%M:%ST%Y-%m-%d")
        artifact["annotations"][j]["timestamp"] = annotation_date_object

    artifact["timestamp"] = date_obj
    return obj

# Sanitizes objects to be JSON-friendly 
def sanitize_object(obj, fs): #Converts objects that can't be passed on into the GUI into a JSON-friendly format
    if(obj.get("type") == "screenshot"): #Checks if object is a screenshot artifact
        image_id = obj.get("screenshot_file")
        image = base64.b64encode(fs.get(image_id).read()) #Gets image data from DB and encodes it into base64
        obj["screenshot_file"] = image.decode() #Base 64 is turned into a string and replaces the objectID

    if(obj.get("type") == "network_activity"):
        start_time = obj.get("start_time")
        end_time = obj.get("end_time")
        start_time_str = start_time.strftime("%H:%M:%ST%Y-%m-%d")
        end_time_str = end_time.strftime("%H:%M:%ST%Y-%m-%d")
        obj["start_time"] = start_time_str
        obj["end_time"] = end_time_str

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
    return obj

# Encodes file into a base64 string 
def file_encoder(file_path):
    file = open(file_path, "rb") # opening for [r]eading as [b]inary
    file_bytes = file.read() # if you only wanted to read 512 bytes, do .read(512)
    file.close()
    file_base64 = base64.b64encode(file_bytes)
    file_base64_str= file_base64.decode()
    return file_base64_str

# Decodes file and writes data into a file
def file_decoder(post_request, new_file_path_absolute):
    file_dict = post_request.json()
    file_str = file_dict.get("file")
    file_base64_bytes = file_str.encode('utf-8')
    file_bytes = base64.b64decode(file_base64_bytes)
    file = open(new_file_path_absolute, "wb")
    file.write(file_bytes)

# Returns global variable counters that keep track of sync status
def get_sync_status():
    total, used, free = shutil.disk_usage("/") # Gets storage info 
    free = round(free / (2**30), 2)
    used = round(used / (2**30), 2)
    total = round(total / (2**30), 2)

    sync_status = {
        "keystroke_total_count": keystroke_total_count,
        "mouse_action_total_count": mouse_action_total_count,
        "screenshot_total_count": screenshot_total_count,
        "process_total_count": process_total_count,
        "window_history_total_count": window_history_total_count,
        "system_call_total_count": system_call_total_count,
        "video_total_count": video_total_count,
        "network_activity_total_count": network_activity_total_count,
        "artifact_total_count": artifact_total_count,
        "keystroke_counter": keystroke_counter,
        "mouse_action_counter": mouse_action_counter,
        "screenshot_counter": screenshot_counter,
        "process_counter": process_counter,
        "window_history_counter": window_history_counter,
        "system_call_counter": system_call_counter,
        "video_counter": video_counter,
        "network_activity_counter": network_activity_counter,
        "artifact_counter": artifact_counter,
        "total_storage": total,
        "used_storage": used,
        "free_storage": free
    }
    
    return sync_status

# Gets all object ids from all relevant collections for sync 
def get_all_artifact_ids():
    client = MongoClient(port=27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)
    dbs = database.DatabaseService(client, db, fs)

    id_json = dbs.get_all_object_ids() # Gets all object IDs from all the artifact collections
    id_json["ips"] =  dbs.get_all_ips() # Gets all stored IPs in database
    id_json["macs"] = dbs.get_all_macs() # Gets all stored MACs in database
    id_json["tags"] = dbs.get_all_tags() # Gets all stored tags in database
 
    return id_json

# Gets post request to get files from local filesystem
def get_file(request):
    file_str = file_encoder(request.get("path")) # Gets file encoded in base64 to send over HTTP 
    file_json = { "file": file_str }

    return file_json

# Updates global variables to signal to stop sync for certain or all artifacts
def cancel_sync(request):
    global keystroke_active
    global mouse_action_active
    global screenshot_active
    global process_active
    global window_history_active
    global system_call_active
    global video_active
    global network_activity_active

    print(request)
    keystroke_active = request.get("keystroke")
    mouse_action_active = request.get("mouse_action")
    screenshot_active = request.get("screenshot")
    process_active = request.get("process")
    window_history_active = request.get("window_history")
    system_call_active = request.get("system_call")
    video_active = request.get("video")
    network_activity_active = request.get("network_activity")

def receive_artifact_from_sync(artifact, host_ip_address):
    client = MongoClient(port=27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)
    dbs = database.DatabaseService(client, db, fs)

    if artifact.get("type") == "keystroke":
        artifact = desanitize_object(artifact, fs)
        db.Keystroke.insert_one(artifact)

    elif artifact.get("type") == "mouse_action":
        artifact = desanitize_object(artifact, fs)
        db.MouseAction.insert_one(artifact)

    elif artifact.get("type") == "screenshot":
        artifact = desanitize_object(artifact, fs)
        image_bytes = artifact.get("screenshot_file")
        screenshot_file_id = fs.put(image_bytes)
        artifact["screenshot_file"] = screenshot_file_id
        db.Screenshot.insert_one(artifact)

    elif artifact.get("type") == "video":
        artifact = desanitize_object(artifact, fs)
        old_file_path = artifact.get("video_file_link")
        old_file_path_list = old_file_path.split("/")
        filename = old_file_path_list[-1]
        new_file_path_relative = "./videos/" + filename
        new_file_path_absolute = os.path.abspath(new_file_path_relative)
        target_url = "http://" + host_ip_address + ":5000/get_file"
        sender_info = { "ip_addr": host_ip_address, "path": old_file_path}
        print(target_url)
        post_request = requests.post(target_url, json = sender_info)
        if not os.path.isdir('./videos'):  # Checks if dir exists
        # Creates one if it doesn't
            os.mkdir('./videos/')

        file_decoder(post_request, new_file_path_absolute)
        video_symlink(filename, new_file_path_absolute)
        db.Video.insert_one(artifact)

    elif artifact.get("type") == "network_activity":
        artifact = desanitize_object(artifact, fs)
        filename = artifact.get("PCAPFile")
        new_file_path_relative = "./pcap/" + filename
        new_file_path_absolute = os.path.abspath(new_file_path_relative)
        target_url = "http://" + host_ip_address + ":5000/get_file"
        old_file_path = "./pcap/" + filename
        sender_info = { "ip_addr": host_ip_address, "path": old_file_path}
        print(target_url)
        post_request = requests.post(target_url, json = sender_info)
        if not os.path.isdir('./pcap'):  # Checks if dir exists
        # Creates one if it doesn't
            os.mkdir('./pcap/')

        file_decoder(post_request, new_file_path_absolute)
        db.NetworkActivity.insert_one(artifact)
        print(artifact)

    elif artifact.get("type") == "window_history":
        artifact = desanitize_object(artifact, fs)
        db.WindowHistory.insert_one(artifact)

    elif artifact.get("type") == "process":
        artifact = desanitize_object(artifact, fs)
        db.Process.insert_one(artifact)

    elif artifact.get("type") == "system_call":
        artifact = desanitize_object(artifact, fs)
        db.SystemCall.insert_one(artifact)

    elif artifact.get("ips"):
        ip_list = artifact.get("ips")
        for i in range(len(ip_list)):
            dbs.add_ip(ip_list[i])

    elif artifact.get("macs"):
        macs_list = artifact.get("macs")
        for i in range(len(macs_list)):
            dbs.add_mac(macs_list[i])

    elif artifact.get("tags"):
        tags_list = artifact.get("tags")
        for i in range(len(tags_list)):
            dbs.add_tag(tags_list[i])

    else:
        print("Not a vaild artifact")

    print(artifact)
# This method gets artifacts to send over to target
def get_artifact_to_sync(target_id_dict, target_url, artifacts_to_sync):
    # Global variables to keep track out status of sync
    global keystroke_total_count
    global mouse_action_total_count
    global screenshot_total_count
    global process_total_count
    global window_history_total_count
    global system_call_total_count
    global video_total_count
    global network_activity_total_count
    global artifact_total_count
    global keystroke_counter
    global mouse_action_counter
    global screenshot_counter
    global process_counter
    global window_history_counter
    global system_call_counter
    global video_counter
    global network_activity_counter
    global artifact_counter
    global keystroke_active
    global mouse_action_active
    global screenshot_active
    global process_active
    global window_history_active
    global system_call_active
    global video_active
    global network_activity_active

    client = MongoClient(port=27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)
    dbs = database.DatabaseService(client, db, fs)

    # Gets all artifact ids from current machine
    my_id_dict = get_all_artifact_ids()
    my_keystroke_list = my_id_dict.get("keystroke_id_list")
    my_mouse_action_list = my_id_dict.get("mouse_action_id_list")
    my_screenshot_list = my_id_dict.get("screenshot_id_list")
    my_process_list = my_id_dict.get("process_id_list")
    my_window_history_list = my_id_dict.get("window_history_id_list")
    my_system_call_list = my_id_dict.get("system_call_id_list")
    my_video_list = my_id_dict.get("video_id_list")
    my_network_activity_list = my_id_dict.get("network_activity_id_list")
    
    # Gets all artifact ids from target machine
    target_id_dict = json.loads(target_id_dict.decode('utf-8'))
    target_keystroke_list = target_id_dict.get("keystroke_id_list")
    target_mouse_action_list = target_id_dict.get("mouse_action_id_list")
    target_screenshot_list = target_id_dict.get("screenshot_id_list")
    target_process_list = target_id_dict.get("process_id_list")
    target_window_history_list = target_id_dict.get("window_history_id_list")
    target_system_call_list = target_id_dict.get("system_call_id_list")
    target_video_list = target_id_dict.get("video_id_list")
    target_network_activity_list = target_id_dict.get("network_activity_id_list")

    # Compares id lists list to determine which artifacts need to be sent 
    keystroke_to_query = list(set(my_keystroke_list) - set(target_keystroke_list))
    mouse_action_to_query = list(set(my_mouse_action_list) - set(target_mouse_action_list))
    screenshot_to_query = list(set(my_screenshot_list) - set(target_screenshot_list))
    process_to_query = list(set(my_process_list) - set(target_process_list))
    window_history_to_query = list(set(my_window_history_list) - set(target_window_history_list))
    system_call_to_query = list(set(my_system_call_list) - set(target_system_call_list))
    video_to_query = list(set(my_video_list) - set(target_video_list))
    network_activity_to_query = list(set(my_network_activity_list) - set(target_network_activity_list))

    # Total numbers for artifacts to sync 
    keystroke_total_count = len(keystroke_to_query)
    mouse_action_total_count = len(mouse_action_to_query)
    screenshot_total_count = len(screenshot_to_query)
    process_total_count = len(process_to_query)
    window_history_total_count = len(window_history_to_query)
    system_call_total_count = len(system_call_to_query)
    video_total_count = len(video_to_query)
    network_activity_total_count = len(network_activity_to_query)
    artifact_total_count = keystroke_total_count + mouse_action_total_count + screenshot_total_count + process_total_count + window_history_total_count + system_call_total_count + video_total_count + network_activity_total_count

    # Artifact counters for sync status 
    keystroke_counter = 0
    mouse_action_counter = 0
    screenshot_counter = 0
    process_counter = 0
    window_history_counter = 0
    system_call_counter = 0
    video_counter = 0
    network_activity_counter = 0
    artifact_counter = 0

    # Artifact global variables to cancel sync in real time
    keystroke_active = True
    mouse_action_active = True
    screenshot_active = True
    process_active = True
    window_history_active = True
    system_call_active = True
    video_active = True
    network_activity_active = True

    ips_to_send = dbs.get_all_ips()
    macs_to_send = dbs.get_all_macs()
    tags_to_send = dbs.get_all_tags()
    ip_json = {"ips": ips_to_send} 
    mac_json = {"macs": macs_to_send}
    tags_json = {"tags": tags_to_send}
    post_request = requests.post(target_url, json = ip_json) # Sends stored IPs in database
    post_request = requests.post(target_url, json = mac_json) # Sends stored MACs in database
    post_request = requests.post(target_url, json = tags_json) # Sends stored tags in database

    if artifacts_to_sync.get("keystroke"): # Checks if artifact is selected to 
        for i in range(keystroke_total_count):
            if not keystroke_active: # Checks if cancel sync button is selected to stop sync for specific artifact
                break
            keystroke_counter += 1 # Updates counter for artifact sync
            artifact_counter += 1 # Updates total counter for artifacts 
            artifact = dbs.database_query_id(keystroke_to_query[i]) # Queries database for artifact
            artifact_json = sanitize_object(artifact, fs) # Sanitizes object to a JSON-friendly format
            print("Keystroke Sync: " + str(keystroke_counter) + "/" + str(keystroke_total_count))
            post_request = requests.post(target_url, json = artifact_json) # Sends artifact info in a post request

    if artifacts_to_sync.get("mouse_action"):
        for i in range(mouse_action_total_count):
            if not mouse_action_active:
                break
            mouse_action_counter += 1 
            artifact_counter += 1
            artifact = dbs.database_query_id(mouse_action_to_query[i])
            artifact_json = sanitize_object(artifact, fs)
            print("Mouse Action Sync: " + str(mouse_action_counter) + "/" + str(mouse_action_total_count))
            post_request = requests.post(target_url, json = artifact_json)

    if artifacts_to_sync.get("screenshot"):
        for i in range(screenshot_total_count):
            if not screenshot_active:
                break
            screenshot_counter += 1
            artifact_counter += 1
            artifact = dbs.database_query_id(screenshot_to_query[i])
            artifact_json = sanitize_object(artifact, fs)
            print("Screenshot Sync: " + str(screenshot_counter) + "/" + str(screenshot_total_count))
            post_request = requests.post(target_url, json = artifact_json)

    if artifacts_to_sync.get("process"):
        for i in range(process_total_count):
            if not process_active:
                break
            process_counter += 1
            artifact_counter += 1
            artifact = dbs.database_query_id(process_to_query[i])
            artifact_json = sanitize_object(artifact, fs)
            print("Process Sync: " + str(process_counter) + "/" + str(process_total_count))
            post_request = requests.post(target_url, json = artifact_json)

    if artifacts_to_sync.get("window_history"):
        for i in range(window_history_total_count):
            if not window_history_active:
                break
            window_history_counter += 1
            artifact_counter += 1
            artifact = dbs.database_query_id(window_history_to_query[i])
            artifact_json = sanitize_object(artifact, fs)
            print("Window History Sync: " + str(window_history_counter) + "/" + str(window_history_total_count))
            post_request = requests.post(target_url, json = artifact_json)

    if artifacts_to_sync.get("system_call"):
        for i in range(system_call_total_count):
            if not system_call_active:
                break
            system_call_counter += 1
            artifact_counter += 1
            artifact = dbs.database_query_id(system_call_to_query[i])
            artifact_json = sanitize_object(artifact, fs)
            print("System Call Sync: " + str(system_call_counter) + "/" + str(system_call_total_count))
            post_request = requests.post(target_url, json = artifact_json)

    if artifacts_to_sync.get("video"):
        for i in range(video_total_count):
            if not video_active:
                break
            video_counter += 1
            artifact_counter += 1
            artifact = dbs.database_query_id(video_to_query[i])
            artifact_json = sanitize_object(artifact, fs)
            print("Video Sync: " + str(video_counter) + "/" + str(video_total_count))
            post_request = requests.post(target_url, json = artifact_json)

    if artifacts_to_sync.get("network_activity"):
        for i in range(network_activity_total_count):
            if not network_activity_active:
                break
            network_activity_counter += 1
            artifact_counter += 1
            artifact = dbs.database_query_network_activity(network_activity_to_query[i])
            artifact_json = sanitize_object(artifact, fs)
            print("Network Activity Sync: " + str(network_activity_counter) + "/" + str(network_activity_total_count))
            post_request = requests.post(target_url, json = artifact_json)

    print("Sync is complete")

def start_sync(request):
    # Get IP Address from frontend 
    
    target_ip_address = request.get("target_ip")
    artifacts_to_sync = request.get("artifacts_to_sync")
    target_port = "5000"
    target_request = "/get_all_artifact_ids"
    target_url = "http://" + target_ip_address + ":" + target_port + target_request # Creating URL for POST request to get all artifact IDS
    post_request = requests.post(target_url) # Sending POST request
    target_url_get_artifacts = "http://" + target_ip_address + ":" + target_port + "/receive_artifact_from_sync"  # URL for receiver end
    get_artifact_to_sync(post_request.content, target_url_get_artifacts, artifacts_to_sync)

    response = {
        "text": "Sync starting...",
        "total_artifacts_to_sync": 0,
        "artifacts_synced_so_far": 0,
        "syncing_with": target_ip_address,
    }
    return response
