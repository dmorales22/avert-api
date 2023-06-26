# This file is used for the primary CRUD operations for the AVERT backend.
from pymongo import MongoClient
import gridfs
import datetime
from bson import ObjectId
import subprocess
import pyshark
import os

# This section are helper methods for the DatabaseService class

# Signature: string add_path(string filename)
# Author: Jose Rodriguez
# Purpose: This method is to create a filename path for PCAPs.
# Pre-condition:  @requires filename != None
# Post-condition: @ensures \result returns combined string.


def add_path(filename):
    return "./pcap/" + filename


"""
Given a list of fields, and an expression_query, returns the query needed
to field the expression across all the fields.


e.g:
    fields = ["a", "b", "c"]
    expression_query = "192.*.*.*"

    returns:
    {"$or" : [{"a": {"$regex": "192.*.*.*", "$options": "i"}}, {"b": ...}, {"c": ...}]}
"""

# Signature: string build_query_for_fields(list[string] fields, string expression_query)
# Author: Jose Rodriguez
# Purpose: This is a helper method is for regex queries for the database_query method.
# Pre-condition:  @requires fields && expression_query != None
# Post-condition: @ensures \result Returns regex expression query.


def build_query_for_fields(fields, expression_query):
    return {
        '$or': [{field: {
                "$regex": expression_query, "$options": "i"
                }} for field in fields]
    }

# Signature: string add_absolute_path(string filename)
# Author: Jose Rodriguez
# Purpose: This is a helper method to get the absolute path of a file.
# Pre-condition:  @requires filename != None
# Post-condition: @ensures \result Returns absolute filepath.


def add_absolute_path(filename):
    filename_with_path = add_path(filename)
    return os.path.abspath(filename_with_path)

# Signature: dict dissect_network_activity(dict network_activity)
# Author: Jose Rodriguez
# Purpose: This is a helper method to dissect network packets from PCAP files.
# Pre-condition:  @requires network_activity != None
# Post-condition: @ensures \result Dissects packets into 'summary' and 'content' attributes.
#                @ensures \result Is a dictionary of dissected packets


def dissect_network_activity(network_activity):
    out = {}
    out['start_time'] = network_activity['start_time']
    out['end_time'] = network_activity['end_time']
    out['_id'] = str(network_activity['_id'])
    out['id'] = str(network_activity['_id'])
    out['artifact'] = network_activity['artifact']
    out['type'] = network_activity['type']
    out['summary'] = network_activity['summary']

    absolute_filepath = add_absolute_path(network_activity['PCAPFile'])

    packets = []

    summaries_cap = pyshark.FileCapture(absolute_filepath, only_summaries=True)
    cap = pyshark.FileCapture(absolute_filepath)
    for packet, summary_packet in zip(cap, summaries_cap):
        packet = {
            'summary': str(summary_packet),
            'content': str(packet)
        }
        packets.append(packet)

    out['packets'] = packets
    return out

# Signature: dict add_to_unique_list(int 1, string element)
# Author: Jose Rodriguez
# Purpose: This is a helper method to dissect network packets from PCAP files.
# Pre-condition:  @requires network_activity != None
# Post-condition: @ensures \result Dissects packets into 'summary' and 'content' attributes.
#                @ensures \result Is a dictionary of dissected packets


def add_to_unique_list(l, element):
    return list(set(l + [element]))

# This class is used for the CRUD operations for the AVERT backend


class DatabaseService:
    # Passes in client, database, and GridFS (for larger files) objects to use
    def __init__(self, client, db, fs):
        self.client = client
        self.db = db
        self.fs = fs
        self.ips = set()
        self.macs = set()
        self.tags = set()

    # Signature: dict get_all_object_ids(void)
    # Author: David Morales
    # Purpose: To retrieve all objectIDs from each collection and return a dictionary of lists for syncing
    # Pre-condition:  @requires id_list != None
    # Post-condition: @ensures \result id_info_dict != None
    #                @ensures \result _id != None
    #                @ensures \result id_info_dict has all string objectIDs

    def get_all_object_ids(self):  # Gets all objectIDs from all collections
        keystroke_id_list = [str(id)
                             for id in self.db.Keystroke.find().distinct('_id')]
        mouse_action_id_list = [
            str(id) for id in self.db.MouseAction.find().distinct('_id')]
        screenshot_id_list = [
            str(id) for id in self.db.Screenshot.find().distinct('_id')]
        process_id_list = [str(id)
                           for id in self.db.Process.find().distinct('_id')]
        window_history_id_list = [
            str(id) for id in self.db.WindowHistory.find().distinct('_id')]
        system_call_id_list = [
            str(id) for id in self.db.SystemCall.find().distinct('_id')]

        #command_history_id_list = [str(id) for id in self.db.CommandHistory.find().distinct('_id')]
        video_id_list = [str(id)
                         for id in self.db.Video.find().distinct('_id')]
        network_activity_id_list = [
            str(id) for id in self.db.NetworkActivity.find().distinct('_id')]

        id_info_dict = {  # Creates a JSON-friendly dictionary of all list of objectIDs
            "keystroke_id_list": keystroke_id_list,
            "mouse_action_id_list": mouse_action_id_list,
            "screenshot_id_list": screenshot_id_list,
            "process_id_list": process_id_list,
            "window_history_id_list": window_history_id_list,
            "system_call_id_list": system_call_id_list,
            "video_id_list": video_id_list,
            "network_activity_id_list": network_activity_id_list
        }

        return id_info_dict

    # Signature: void configuration_db_write(bool keystroke, bool mouse_action, bool process, bool window_history, bool video, bool network_activity)
    # Author: David Morales
    # Purpose: To write configuration settings to the database
    # Pre-condition:  @requires keystroke and mouse_action and screenshot and process and window_history and system_call and video and network_activity != None
    # Post-condition: @ensures \result db.Configuration is updated
    #                @ensures \result db.Configuration has at least one entry
    def configuration_db_write(self, keystroke, mouse_action, screenshot, process, window_history, system_call, video, network_activity):
        result = self.db.Configuration.update({"_id": 1}, {
            'keystrokes': keystroke,
            'mouse_actions': mouse_action,
            'screenshot': screenshot,
            'process': process,
            'window_history': window_history,
            'system_call': system_call,
            'video': video,
            'network_activity': network_activity
        }, upsert=True)

    # Signature: dict configuration_db_get(void)
    # Author: David Morales
    # Purpose: To get configuration settings from the database
    # Pre-condition:  @requires db.Configuration != None
    # Post-condition: @ensures \result db.Configuration is returned in a dictionary
    #                @ensures \result Creates db.Configuration entry if entry does not exist
    def configuration_db_get(self):
        result = self.db.Configuration.find_one()
        if result != None:
            return result

        keystrokes = True
        mouse_actions = True
        screenshot = True
        process = True
        window_history = True
        system_call = True
        video = False
        network_activity = False

        self.configuration_db_write(
            keystrokes, mouse_actions, screenshot, process, window_history, system_call, video, network_activity)

        return self.configuration_db_get()

    # Signature: void userprofile_db_write(string ip_address, string mac_address)
    # Author: David Morales
    # Purpose: This method writes a user profile to database.
    # Pre-condition:  @requires ip_address and mac_address != None
    # Post-condition: @ensures \result db.UserProfile entry is added
    #                @ensures \result prints result of database insertion
    def userprofile_db_write(self, ip_address, mac_address):
        userProfile = {
            "ip_address": ip_address,
            "mac_address": mac_address
        }
        result = self.db.UserProfile(userProfile)
        print(result)

    # Signature: dict get_all_ips(void)
    # Author: Jose Rodriguez
    # Purpose: This method is to get all recorded IP addresses from the database.
    # Pre-condition:  @requires db.AllIPs != None
    # Post-condition: @ensures \result returns all IP addresses stored in the database.
    #                @ensures \result prints result of database insertion
    def get_all_ips(self):
        ips = self.db.AllIPs.find_one({})
        if ips == None:
            self.db.AllIPs.insert_one({'ips': []})
            ips = self.db.AllIPs.find_one({})

        self.ips = set(ips['ips'])
        print(ips['ips'])
        return ips['ips']

    # Signature: dict get_all_macs(void)
    # Author: Jose Rodriguez
    # Purpose: This method is to get all recorded MAC addresses from the database.
    # Pre-condition:  @requires db.AllMACs != None
    # Post-condition: @ensures \result returns all MAC addresses stored in the database.
    #                @ensures \result prints result of database insertion
    def get_all_macs(self):
        macs = self.db.AllMACs.find_one({})

        if macs == None:
            self.db.AllMACs.insert_one({'macs': []})
            macs = self.db.AllMACs.find_one({})

        self.macs = set(macs['macs'])
        return macs['macs']

    # Signature: dict get_all_tags(void)
    # Author: Jose Rodriguez
    # Purpose: This method is to get all recorded tags from the database.
    # Pre-condition:  @requires db.AllTags != None
    # Post-condition: @ensures \result returns all tags addresses stored in the database.
    #                @ensures \result prints result of database insertion
    def get_all_tags(self):
        tags = self.db.AllTags.find_one({})

        if tags == None:
            self.db.AllTags.insert_one({'tags': []})
            tags = self.db.AllTags.find_one({})

        self.tags = set(tags['tags'])
        print("here", tags['tags'])
        return tags['tags']

    # Signature: void add_ip(string ip)
    # Author: Jose Rodriguez
    # Purpose: This method is to add IP addresses to the database.
    # Pre-condition:  @requires ip != None
    #                @requires ip is not in self.ips
    # Post-condition: @ensures \result Updates current IP list with the new IP address to database.
    #                @ensures \result Creates new collection in the database if it does not exist
    #                @ensures \result Adds new IP address to current set.
    def add_ip(self, ip):
        if ip in self.ips:
            return

        ips = self.db.AllIPs.find_one({})

        if ips == None:
            self.db.AllIPs.insert_one({"ips": []})
            ips = self.db.AllIPs.find_one({})

        self.db.AllIPs.update({'_id': ips['_id']}, {
                              '$set': {'ips': add_to_unique_list(ips['ips'], ip)}})
        self.ips.add(ip)

    # Signature: void add_mac(string mac)
    # Author: Jose Rodriguez
    # Purpose: This method is to add MAC addresses to the database.
    # Pre-condition:  @requires mac != None
    #                @requires mac is not in self.macs
    # Post-condition: @ensures \result Updates current MAC list with the new MAC address to database.
    #                @ensures \result Creates new collection in the database if it does not exist
    #                @ensures \result Adds new MAC address to current set.
    def add_mac(self, mac):
        if mac in self.macs:
            return

        macs = self.db.AllMACs.find_one({})

        if macs == None:
            self.db.AllMACs.insert_one({"macs": []})
            macs = self.db.AllMACs.find_one({})

        self.db.AllMACs.update({'_id': macs['_id']}, {
                               '$set': {'macs': add_to_unique_list(macs['macs'], mac)}})
        self.macs.add(mac)

    # Signature: void add_tag(string tag)
    # Author: Jose Rodriguez
    # Purpose: This method is to add new tags to the database.
    # Pre-condition:  @requires tag != None
    #                @requires tag is not in self.tags
    # Post-condition: @ensures \result Updates current tags list with the new tag to database.
    #                @ensures \result Creates new collection in the database if it does not exist
    #                @ensures \result Adds new tags to current set.
    def add_tag(self, tag):
        if tag in self.tags:
            return

        tags = self.db.AllTags.find_one({})
        print(tag)

        if tags == None:
            self.db.AllTags.insert_one({"tags": []})
            tags = self.db.AllTags.find_one({})

        self.db.AllTags.update({'_id': tags['_id']}, {
                               '$set': {'tags': add_to_unique_list(tags['tags'], tag)}})
        self.tags.add(tag)

    # Signature: list[dict] database_query(string query)
    # Author: David Morales
    # Purpose: This method queries database using the custom query we have defined.
    # Pre-condition:  @requires query != None
    # Post-condition: @ensures \result Returns a list of all queried artifacts as list of dictionaries.
    #                @ensures \result Returns a list of queried artifacts within query parameters
    #                @ensures \result Prints query request
    def database_query(self, query):  # This method queries the database
        print("Query:", query)
        query_conditions = {}
        type_of_query = query["types"]

        if query["ip_addresses"]:  # Checks if IP address list is populated to add to query expression
            query_conditions["artifact.user_profile.ip_address"] = {
                '$in': query["ip_addresses"]}

        if query["mac_addresses"]:
            query_conditions["artifact.user_profile.mac_address"] = {
                '$in': query["mac_addresses"]}

        if query["time_range"] and query["time_range"][0] != None:
            beginning_date_str = query["time_range"][0]
            print(beginning_date_str)
            beginning_date = datetime.datetime.strptime(
                beginning_date_str[:-5], "%Y-%m-%dT%H:%M:%S")

            if query["time_range"][1] == None:  # Checks if second range is null
                time_range = {
                    '$gte': beginning_date
                }
            else:  # Adds range of query
                end_date_str = query["time_range"][1]
                end_date = datetime.datetime.strptime(
                    end_date_str[:-5], "%Y-%m-%dT%H:%M:%S")
                time_range = {
                    '$gte': beginning_date, '$lt': end_date
                }
            query_conditions["artifact.timestamp"] = time_range

        if query["selected_tags"]:  # Searching for tags
            query_conditions["artifact.tags.label"] = {
                '$in': query["selected_tags"]}

        collection = []

        print(query_conditions)
        # checks if query for keystroke is true to add to expression
        if type_of_query["keystroke"]:
            if query["expression"] != '':  # Checks if the expression string is not empty
                fields = ["key_press", "artifact.user_profile.ip_address", "artifact.user_profile.mac_address",
                          "artifact.annotations.description", "artifact.tags.label"]  # Fields for the regex search
                expression_query = build_query_for_fields(
                    fields, query["expression"])  # Gets the constructed regex query
                # Adds regex query to the main query command
                query_conditions["$or"] = expression_query["$or"]

            # queries database of all relevant documents
            for i in self.db.Keystroke.find(query_conditions):
                collection.append(i)  # adds to a list of objects.

        if type_of_query["mouseAction"]:
            if query["expression"] != '':
                fields = ["button", "mouse_action", "mouse_action_value", "artifact.user_profile.ip_address",
                          "artifact.user_profile.mac_address", "artifact.annotations.description", "artifact.tags.label"]
                expression_query = build_query_for_fields(
                    fields, query["expression"])
                query_conditions["$or"] = expression_query["$or"]

            for i in self.db.MouseAction.find(query_conditions):
                collection.append(i)

        if type_of_query["stillScreenshot"]:
            if query["expression"] != '':
                fields = ["screenshot_size", "screenshot_format", "artifact.user_profile.ip_address",
                          "artifact.user_profile.mac_address", "artifact.annotations.description", "artifact.tags.label"]
                expression_query = build_query_for_fields(
                    fields, query["expression"])
                query_conditions["$or"] = expression_query["$or"]

            for i in self.db.Screenshot.find(query_conditions):
                collection.append(i)

        if type_of_query["windowHistory"]:
            if query["expression"] != '':
                fields = ["primary_screen_resolution", "window_position", "minimized", "maximized", "application_name", "windows_style", "window_title", "window_creation_time",
                          "window_destruction_time", "window_id", "artifact.user_profile.ip_address", "artifact.user_profile.mac_address", "artifact.annotations.description", "artifact.tags.label"]
                expression_query = build_query_for_fields(
                    fields, query["expression"])
                query_conditions["$or"] = expression_query["$or"]

            for i in self.db.WindowHistory.find(query_conditions):
                collection.append(i)

        if type_of_query["process"]:
            if query["expression"] != '':
                fields = ["user_name", "process_name", "process_id", "parent_process_id", "start_name", "command", "terminal", "status", "memory_usage", "no_of_threads", "cpu_percentage",
                          "process_privileges", "process_priority", "process_type", "artifact.user_profile.ip_address", "artifact.user_profile.mac_address", "artifact.annotations.description", "artifact.tags.label"]
                expression_query = build_query_for_fields(
                    fields, query["expression"])
                query_conditions["$or"] = expression_query["$or"]

            for i in self.db.Process.find(query_conditions):
                collection.append(i)

        if type_of_query["systemCall"]:
            if query["expression"] != '':
                query_conditions["systemcall_name"] = query["expression"]

            for i in self.db.SystemCall.find(query_conditions):
                collection.append(i)

        if type_of_query["video"]:
            if query["expression"] != '':
                fields = ["video_file_link", "video_name", "video_size", "video_resolution", "video_frame_rate", "video_duration",
                          "artifact.user_profile.ip_address", "artifact.user_profile.mac_address", "artifact.annotations.description", "artifact.tags.label"]
                expression_query = build_query_for_fields(
                    fields, query["expression"])
                query_conditions["$or"] = expression_query["$or"]

            for i in self.db.Video.find(query_conditions):
                collection.append(i)

        if type_of_query["networkPacket"]:
            network_activity_query = {
                "summary": {"$regex": query['expression'], "$options": "i"}
            }

            for i in self.db.NetworkActivity.find(network_activity_query):
                collection.append(i)

        return collection

    # Signature: dict database_query_id(string id)
    # Author: David Morales
    # Purpose: This method queries database of the artifact collections using a string id
    # Pre-condition:  @requires id != None
    # Post-condition: @ensures \result Returns the found artifact.
    #                @ensures \result Returns None if artifact is not found.
    def database_query_id(self, id):
        object_id = ObjectId(id)

        found_obj = self.db.Keystroke.find_one({"_id": object_id})
        if found_obj != None:
            return found_obj

        found_obj = self.db.MouseAction.find_one({"_id": object_id})
        if found_obj != None:
            return found_obj

        found_obj = self.db.Screenshot.find_one({"_id": object_id})
        if found_obj != None:
            return found_obj

        found_obj = self.db.WindowHistory.find_one({"_id": object_id})
        if found_obj != None:
            return found_obj

        found_obj = self.db.Process.find_one({"_id": object_id})
        if found_obj != None:
            return found_obj

        found_obj = self.db.SystemCall.find_one({"_id": object_id})
        if found_obj != None:
            return found_obj

        found_obj = self.db.Video.find_one({"_id": object_id})
        if found_obj != None:
            return found_obj

        found_obj = self.db.NetworkActivity.find_one({"_id": object_id})
        if found_obj != None:
            return dissect_network_activity(found_obj)

        return None

    # Signature: dict database_query_network_activity(string id)
    # Author: David Morales
    # Purpose: This method queries database for Network Activity artifacts using a string id.
    # Pre-condition:  @requires id != None
    # Post-condition: @ensures \result Returns the found artifact.
    #                @ensures \result Returns None if artifact is not found.
    def database_query_network_activity(self, id):
        object_id = ObjectId(id)
        found_obj = self.db.NetworkActivity.find_one({"_id": object_id})
        if found_obj != None:
            return found_obj

        return None

    # Signature: void database_delete_id(string id)
    # Author: Jose Rodriguez
    # Purpose: This method deletes artifact from database just from a string id
    # Pre-condition:  @requires id != None
    # Post-condition: @ensures \result Deletes artifact from database.
    #                @ensures \result Checks if artifact can be deleted.
    #                @ensures \result Prints result of deletion
    def database_delete_id(self, id):
        object = self.database_query_id(id)

        _type = object.get('type')

        if object.get("type") == "keystroke":
            print(f'Artifact type \'{_type}\' is not deletable')

        elif object.get("type") == "mouse_action":
            print('Artifact is not deletable')
            print(f'Artifact type \'{_type}\' is not deletable')

        elif object.get("type") == "screenshot":
            result = self.db.Screenshot.delete_one(object)
            print(f'deleted screenshot with id: {id}')

        elif object.get("type") == "video":
            result = self.db.Video.delete_one(object)
            print(f'deleted video with id: {id}')

        elif object.get("type") == "window_history":
            print(f'Artifact type \'{_type}\' is not deletable')

        elif object.get("type") == "process":
            print(f'Artifact type \'{_type}\' is not deletable')

        elif object.get("type") == "system_call":
            print(f'Artifact type \'{_type}\' is not deletable')

        elif object.get("type") == "network_activity":
            print(object)
            object = self.db.NetworkActivity.find_one(
                {'_id': ObjectId(object['_id'])})
            result = self.db.NetworkActivity.delete_one({'_id': object['_id']})
            print(f'deleted network activity with id: {id}')

        else:
            print("Nothing is deleted")

    # Signature: void keystroke_db_write(string keypress, Datatime timestamp: datetime, dict user_profile, dict tags, dict annotation)
    # Author: David Morales
    # Purpose: This method inserts a Keystroke artifact into the database
    # Pre-condition:  @requires keypress && timestamp: datetime &&user_profile && tags && annotation != None
    # Post-condition: @ensures \result Creates dictionary from parameters.
    #                @ensures \result Inserts Keystroke artifact into database
    #                @ensures \result Prints result of insertion
    def keystroke_db_write(self, keypress, timestamp: datetime, user_profile, tags, annotation):
        artifact = {
            "user_profile": user_profile,
            "timestamp": timestamp,
            "tags": tags,
            "annotations": annotation
        }
        keystroke = {
            "artifact": artifact,
            "key_press": keypress,
            "type": "keystroke"
        }
        result = self.db.Keystroke.insert_one(keystroke)

    # Signature: void mouse_action_db_write(string button, string mouse_action, string mouse_action_value, string active_window, string window_focus, string process, Datetim timestamp, dict user_profile, dict tags, dict annotation)
    # Author: David Morales
    # Purpose: This method inserts a MouseAction artifact into the database
    # Pre-condition:  @requires button && mouse_action && mouse_action_value && active_window && window_focus && process && timestamp && user_profile && tags && annotation != None
    # Post-condition: @ensures \result Creates dictionary from parameters.
    #                @ensures \result Inserts MouseAction artifact into database
    #                @ensures \result Prints result of insertion
    def mouse_action_db_write(self, button, mouse_action, mouse_action_value, active_window, window_focus, process, timestamp, user_profile, tags, annotation):
        artifact = {
            "user_profile": user_profile,
            "timestamp": timestamp,
            "tags": tags,
            "annotations": annotation
        }
        mouseAction = {
            "artifact": artifact,
            "button": button,
            "mouse_action": mouse_action,
            "mouse_action_value": mouse_action_value,
            "active_window": active_window,
            "window_focus": window_focus,
            "process": process,
            "type": "mouse_action"
        }
        result = self.db.MouseAction.insert_one(mouseAction)
        print(result)

    # Signature: void annotation_db_write(string object_id, list[dict] annotation)
    # Author: David Morales
    # Purpose: This method uses an objectID to get artifact and appends new annotation to the object.
    # Pre-condition:  @requires object_id && annotation != None
    # Post-condition: @ensures \result Creates object with new annotation appended.
    #                @ensures \result Replaces artifact with object
    #                @ensures \result Prints result of insertion
    def annotation_db_write(self, object_id, annotation):
        object = self.database_query_id(object_id)
        artifact = object.get("artifact")
        annotation_list = artifact.get("annotations")
        annotation_list.append(annotation)
        object["artifact"]["annotations"] = annotation_list

        object_id = ObjectId(object.get("_id"))
        if object.get("type") == "keystroke":
            del object['_id']
            result = self.db.Keystroke.replace_one({"_id": object_id}, object)

        elif object.get("type") == "mouse_action":
            del object['_id']
            result = self.db.MouseAction.replace_one(
                {"_id": object_id}, object)

        elif object.get("type") == "screenshot":
            del object['_id']
            result = self.db.Screenshot.replace_one({"_id": object_id}, object)

        elif object.get("type") == "window_history":
            del object['_id']
            result = self.db.WindowHistory.replace_one(
                {"_id": object_id}, object)

        elif object.get("type") == "process":
            del object['_id']
            result = self.db.Process.replace_one({"_id": object_id}, object)

        elif object.get("type") == "system_call":
            del object['_id']
            result = self.db.SystemCall.replace_one({"_id": object_id}, object)

        elif object.get("type") == "video":
            del object['_id']
            result = self.db.Video.replace_one({"_id": object_id}, object)

        elif object.get("type") == "network_activity":
            del object['_id']
            result = self.db.NetworkActivity.replace_one(
                {"_id": object_id}, object)
        else:
            print("Nothing here")

    # Signature: void tags_db_write(string object_id, list[dict] tag)
    # Author: David Morales
    # Purpose: This method takes string version of the object id and tag (already formatted) and adds the tag into the object.
    # Pre-condition:  @requires object_id && annotation != None
    # Post-condition: @ensures \result Creates object with new annotation appended.
    #                @ensures \result Replaces artifact with object
    #                @ensures \result Prints result of insertion
    def tags_db_write(self, object_id, tag):
        object = self.database_query_id(object_id)
        artifact = object.get("artifact")
        tag_list = artifact.get("tags")
        tag_list.append(tag)
        object["artifact"]["tags"] = tag_list
        tag_to_add = tag['label']
        self.add_tag(tag_to_add)

        object_id = ObjectId(object.get("_id"))  # Gets artifact by id
        # Checks object type to search in that collection
        if object.get("type") == "keystroke":
            result = self.db.Keystroke.replace_one(
                {"_id": object_id}, object)  # Replaces object

        elif object.get("type") == "mouse_action":
            result = self.db.MouseAction.replace_one(
                {"_id": object_id}, object)

        elif object.get("type") == "screenshot":
            result = self.db.Screenshot.replace_one({"_id": object_id}, object)

        elif object.get("type") == "window_history":
            result = self.db.WindowHistory.replace_one(
                {"_id": object_id}, object)

        elif object.get("type") == "process":
            result = self.db.Process.replace_one({"_id": object_id}, object)

        elif object.get("type") == "system_call":
            result = self.db.SystemCall.replace_one({"_id": object_id}, object)

        elif object.get("type") == "video":
            result = self.db.Video.replace_one({"_id": object_id}, object)

        elif object.get("type") == "network_activity":
            result = self.db.NetworkActivity.replace_one(
                {"_id": object_id}, object)

        else:
            print("Nothing here")

    # Signature: void tags_db_delete(string object_id, list[dict] tag)
    # Author: David Morales
    # Purpose: This method takes string version of the object id and tag (already formatted) and deletes the tag.
    # Pre-condition:  @requires object_id && tags != None
    # Post-condition: @ensures \result Creates object with tag removed.
    #                @ensures \result Replaces artifact with object
    #                @ensures \result Prints result of insertion
    def tags_db_delete(self, object_id, tags):
        object = self.database_query_id(object_id)
        artifact = object.get("artifact")
        tag_list = artifact.get("tags")
        indice = -1

        for i in range(len(tag_list)):
            value = tag_list[i].get("label")
            if value == tags[0]:
                indice = i

        if(indice == -1):
            print("Tag not found")
            return

        del tag_list[indice]
        object["artifact"]["tags"] = tag_list
        object_id = ObjectId(object.get("_id"))

        if object.get("type") == "keystroke":
            result = self.db.Keystroke.replace_one({"_id": object_id}, object)

        elif object.get("type") == "mouse_action":
            result = self.db.MouseAction.replace_one(
                {"_id": object_id}, object)

        elif object.get("type") == "screenshot":
            result = self.db.Screenshot.replace_one({"_id": object_id}, object)

        elif object.get("type") == "window_history":
            result = self.db.WindowHistory.replace_one(
                {"_id": object_id}, object)

        elif object.get("type") == "process":
            result = self.db.Process.replace_one({"_id": object_id}, object)

        elif object.get("type") == "system_call":
            result = self.db.SystemCall.replace_one({"_id": object_id}, object)

        elif object.get("type") == "video":
            result = self.db.Video.replace_one({"_id": object_id}, object)

        elif object.get("type") == "network_activity":
            result = self.db.NetworkActivity.replace_one(
                {"_id": object_id}, object)

        else:
            print("Nothing here")

    # Signature: void screenshot_db_write(bytes screenshot_file, string screenshot_size, string screenshot_format, Datetime timestamp, dict user_profile, list[dict] tags, list[dict] annotation)
    # Author: David Morales
    # Purpose: This method inserts a Screenshot artifact into the database.
    # Pre-condition:  @requires screenshot_file && screenshot_size && screenshot_format && timestamp && user_profile && tags && annotation != None
    # Post-condition: @ensures \result Creates dictionary from parameters.
    #                @ensures \result Inserts Screenshot artifact into database
    #                @ensures \result Prints result of insertion
    def screenshot_db_write(self, screenshot_file, screenshot_size, screenshot_format, timestamp, user_profile, tags, annotation):
        screenshot_file_id = self.fs.put(screenshot_file)
        artifact = {
            "user_profile": user_profile,
            "timestamp": timestamp,
            "tags": tags,
            "annotations": annotation
        }
        stillScreenshot = {
            "artifact": artifact,
            "screenshot_name": "screenshot_name",  # TODO HERE
            "screenshot_file": screenshot_file_id,
            "screenshot_size": screenshot_size,
            "screenshot_format": screenshot_format,
            "type": "screenshot"
        }

        result = self.db.Screenshot.insert_one(stillScreenshot)
        print(result)

    # Signature: dict window_history_db_query(string window_id)
    # Author: David Morales
    # Purpose: This method is to query the window history collection using the window id of the process.
    # Pre-condition:  @requires window_history != None
    # Post-condition: @ensures \result Queries database for matching window_id
    #                @ensures \result Returns WindowHistory artifact as a dictionary
    def window_history_db_query(self, window_id):
        object = self.db.WindowHistory.find_one({"window_id": window_id})
        return object

    # Signature: void window_history_db_update_removed(string window_id)
    # Author: David Morales
    # Purpose: This method updates window history for closed windows to add destruction time.
    # Pre-condition:  @requires window_history && window_destruction_time != None
    # Post-condition: @ensures \result Queries database for matching window_id
    #                @ensures \result Updates matching WindowHistory artifact with its destruction time
    #                @ensures \result Returns WindowHistory artifact as a dictionary
    def window_history_db_update_removed(self, window_id, window_destruction_time):
        object = self.db.WindowHistory.find_one({"window_id": window_id})
        object["window_destruction_time"] = window_destruction_time
        object_id = object.get("_id")
        result = self.db.WindowHistory.replace_one({"_id": object_id}, object)
        print(result)

    # Signature: void window_history_db_update(string window_id)
    # Author: David Morales
    # Purpose: This method updates window history for a WindowHistory artifact.
    # Pre-condition:  @requires window_id && visible && maximized && minimized && window_title && window_destruction_time != None
    # Post-condition: @ensures \result Queries database for matching window_id
    #                @ensures \result Updates matching WindowHistory artifact with updated visible, maximized, minimized, window_title and window_destruction_time attributes
    #                @ensures \result Prints result

    def window_history_db_update(self, window_id, visible, maximized, minimized, window_title, window_destruction_time):
        object = self.db.WindowHistory.find_one({"window_id": window_id})
        object["visible"] = visible
        object["maximized"] = maximized
        object["minimized"] = minimized
        object["window_title"] = window_title
        object["window_destruction_time"] = window_destruction_time
        object_id = object.get("_id")
        result = self.db.WindowHistory.replace_one({"_id": object_id}, object)
        print(result)

    # Signature: void window_history_db_write(string primary_screen_resolution, string window_position, bool visible, string window_placement_command, bool minimized, bool maximized, string applicaton_name, string window_style, string window_title, string window_creation_time, string window_destruction_time, Datetime timestamp, dict user_profile, list[dict] tags, list[dict] annotation, string window_id)
    # Author: David Morales
    # Purpose: This method inserts a WindowHistory artifact into the database.
    # Pre-condition:  @requires primary_screen_resolution && window_position && visible && window_placement_command && minimized && maximized && applicaton_name && window_style && window_title && window_creation_time && window_destruction_time && timestamp && user_profile && tags && annotation && window_id != None
    # Post-condition: @ensures \result Queries database for matching window_id
    #                @ensures \result Updates matching WindowHistory artifact with updated visible, maximized, minimized, window_title and window_destruction_time attributes
    #                @ensures \result Prints result
    def window_history_db_write(self, primary_screen_resolution, window_position, visible, window_placement_command, minimized, maximized, applicaton_name, window_style, window_title, window_creation_time, window_destruction_time, timestamp, user_profile, tags, annotation, window_id):
        artifact = {
            "user_profile": user_profile,
            "timestamp": timestamp,
            "tags": tags,
            "annotations": annotation
        }
        window_history = {
            "artifact": artifact,
            "primary_screen_resolution": primary_screen_resolution,
            "window_position": window_position,
            "visible": visible,
            "window_placement_command": window_placement_command,
            "minimized": minimized,
            "maximized": maximized,
            "application_name": applicaton_name,
            "window_style": window_style,
            "window_title": window_title,
            "window_creation_time": window_creation_time,
            "window_destruction_time": window_destruction_time,
            "window_id": window_id,
            "type": "window_history"
        }

        result = self.db.WindowHistory.insert_one(window_history)
        print(result)

    # Signature: void process_db_write(string user_name, string process_name, string process_id, string parent_process_id, string start_time, string command, string terminal, string status, string memory_usage, int no_of_threads, string pu_percentage, string process_privileges, string process_priority, string process_type, Datetime timestamp, dict user_profile, list[dict] tags, list[dict] annotation)
    # Author: David Morales
    # Purpose: This method inserts a Process artifact into the database.
    # Pre-condition:  @requires user_name && process_name && process_id && parent_process_id && start_time && command && terminal && status && memory_usage && no_of_threads && cpu_percentage && process_privileges && process_priority && process_type && timestamp && user_profile && tags && annotation && window_id != None
    # Post-condition: @ensures \result Creates dictionary from parameters.
    #                @ensures \result Inserts Process artifact into database
    #                @ensures \result Prints result of insertion
    def process_db_write(self, user_name, process_name, process_id, parent_process_id, start_time, command, terminal, status, memory_usage, no_of_threads, cpu_percentage, process_privileges, process_priority, process_type, timestamp, user_profile, tags, annotation):
        artifact = {
            "user_profile": user_profile,
            "timestamp": timestamp,
            "tags": tags,
            "annotations": annotation
        }
        process = {
            "artifact": artifact,
            "user_name": user_name,
            "process_name": process_name,
            "process_id": process_id,
            "parent_process_id": parent_process_id,
            "start_time": start_time,
            "command": command,
            "terminal": terminal,
            "status": status,
            "memory_usage": memory_usage,
            "no_of_threads": no_of_threads,
            "cpu_percentage": cpu_percentage,
            "process_privileges": process_privileges,
            "process_priority": process_priority,
            "process_type": process_type,
            "type": "process"
        }
        result = self.db.Process.insert_one(process)
        print(result)

    # Signature: void systemcall_db_write(string syscall_name, list[string] syscall_args, dict user_profile, list[dict] tags, list[dict] annotation)
    # Author: David Morales
    # Purpose: This method updates window history for a SystemCall artifact.
    # Pre-condition:  @requires syscall_name && syscall_args && timestamp && user_profile && tags && annotation != None
    # Post-condition: @ensures \result Creates dictionary from parameters.
    #                @ensures \result Inserts System artifact into database
    #                @ensures \result Prints result of insertion
    def systemcall_db_write(self, syscall_name, syscall_args, timestamp, user_profile, tags, annotation):
        artifact = {
            "user_profile": user_profile,
            "timestamp": timestamp,
            "tags": tags,
            "annotations": annotation
        }
        system_call = {
            "artifact": artifact,
            "systemcall_name": syscall_name,
            "systemcall_args": syscall_args,
            "type": "system_call"
        }

        result = self.db.SystemCall.insert_one(system_call)
        print(result)

    # Signature: void network_activity_db_write(string PCAPFile, Datetime start_time, Datetime end_time, dict user_profile, list[dict] tags, list[dict] annotation, string summary)
    # Author: David Morales
    # Purpose: This method inserts a NetworkActivity artifact into the database.
    # Pre-condition:  @requires PCAPFile && start_time && end_time && timestamp && user_profile && tags && annotation && summary != None
    # Post-condition: @ensures \result Creates dictionary from parameters.
    #                @ensures \result Inserts NetworkActivity artifact into database
    #                @ensures \result Prints result of insertion
    def network_activity_db_write(self, PCAPFile, start_time, end_time, user_profile, tags, annotation, summary):
        artifact = {
            "user_profile": user_profile,
            "timestamp": start_time,
            "tags": tags,
            "annotations": annotation
        }
        networkActivity = {
            'artifact': artifact,
            "PCAPFile": PCAPFile,
            "start_time": start_time,
            "end_time": end_time,
            "summary": summary,
            "type": "network_activity",
        }
        result = self.db.NetworkActivity.insert_one(networkActivity)
        print(result)

    # Signature: void video_db_write(string video_file_link, string video_name, string video_size, string video_resolution, string video_frame_rate, string video_duration, dict user_profile, list[dict] tags, list[dict] annotation, string summary)
    # Author: David Morales
    # Purpose: This method inserts a Video artifact into the database.
    # Pre-condition:  @requires video_file_link && video_name && video_size && video_resolution && video_frame_rate && video_duration && timestamp && user_profile && tags && annotation && summary != None
    # Post-condition: @ensures \result Creates dictionary from parameters.
    #                @ensures \result Creates symlink in GUI folder
    #                @ensures \result Inserts Video artifact into database
    #                @ensures \result Prints result of insertion
    def video_db_write(self, video_file_link, video_name, video_size, video_resolution, video_frame_rate, video_duration, timestamp, user_profile, tags, annotation):
        #video_file_id = self.fs.put(video_file)
        if not os.path.isdir('../avert-gui/public/videos/'):  # Checks if dir exists
            # Creates one if it doesn't
            os.mkdir('../avert-gui/public/videos/')

        # Runs command to create symlink to public/videos/ dir
        command = ["ln", "-s", video_file_link,
                   "../avert-gui/public/videos/" + video_name]
        run_command = subprocess.Popen(command, stdout=subprocess.PIPE)

        artifact = {
            "user_profile": user_profile,
            "timestamp": timestamp,
            "tags": tags,
            "annotations": annotation
        }
        video = {
            "artifact": artifact,
            "video_file_link": video_file_link,
            "video_name": video_name,
            "video_size": video_size,
            "video_resolution": video_resolution,
            "video_frame_rate": video_frame_rate,
            "video_duration": video_duration,
            "type": "video"
        }

        result = self.db.Video.insert_one(video)
        print(result)
