import os
from typing import List
from flask import Flask, json, request, jsonify
from flask_cors import CORS
from artifact_endpoint import get_artifact
from ip_addresses_endpoint import get_all_ip_addresses
from mac_addresses_endpoint import get_all_mac_addresses
from script_handler import ScriptHandler
from tags_endpoint import get_all_tags, delete_tags, new_tag
from search_endpoint import search
from annotation_endpoint import annotate
from configuration_endpoint import recording_settings, update_recording_settings
from keylogger import KeyLogger
from artifacts.meta_data_helper import MetaDataHelper
from mouselogger import MouseLogger
from processes import Processes
from window_history import WindowHistory
from pymongo import MongoClient
from screenshot_taker import take_screenshot
from deleter import delete_ids
from pcap_exporter import get_pcap
import database
import gridfs
from command_history import CommandHistory
from threading import Thread
import threading
from screenshot_keystroke_listener import ScreenshotKeyLogger
from screenshot_mouse_listener import ScreenshotMouseListener
from network_activity import continuously_record_network_activity
from video_recording_handler import VideoRecordingHandler
from proportional_visualization_endpoint import generate_proportional_visualization
from timeline_visualization_endpoint import generate_timeline_visualization
from sync import start_sync, get_all_artifact_ids, get_artifact_to_sync, get_sync_status, get_file, receive_artifact_from_sync, cancel_sync


"""
This  file is the entry point for the AVERT API HTTP server which is in charge
of serving the different functionality required by the AVERT applciation.

The full scope  of the artifacts is described below.
"""


app = Flask(__name__)
CORS(app)


@app.route('/search', methods=['POST'])
def post_search():  # A request to get search results from the DB of different kinds of artifacts
    """
    The purpose of this function is to return a list with summarized artifacts
    that match a query. Further requests can be made to request more
    information on specific artifacts.

    Signature:

    interface Types {
        stillScreenshot: boolean,
        video: boolean,
        networkPacket: boolean,
        process: boolean,
        keystroke: boolean,
        mouseAction: boolean,
        windowHistory: boolean,
        systemCall: boolean,
        history: boolean,
        log: boolean,
        all: boolean,
        allArtifactTypes: boolean,
    }


    type IPAddresses = List<String>

    type MACAddresses = List<String>

    type TimeRange = List<String>

    type Expression = string

    type SelectedTags = List<String>

    interface SearchQuery {
      types: Types,
      ip_addresses: IPAddresses,
      mac_addresses: MACAddresses,
      time_range: TimeRange,
      expression: Expression,
      selected_tags: SelectedTags,
    };

    interface Summary {
      id: string,
      timestamp: string,
      type: string,
      ip_address: string,
      mac_address: string,
      description: string,
    }


    Signature: List<Summary> post_search(Query)

    Author: David Morales


    Preconditions:
    @requires \forall string field; field in query; query[field] != null
    @requires artifacts.length != 0


    Postconditions:
    @ensures \forall int i; i >= 0 && i < \result.length; \result[i] matches query
    @ensures \forall int i; i >= 0 && i < artifact.length; artifacts[i] matches query <==> \results contains artifacts[i]
    """

    query = request.get_json()
    response = jsonify(search(query))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/artifact', methods=['POST'])
def post_artifact():  # A request to get a specific artifact from the DB using its ID
    """
    The purpose of this function is to return detailed information on an
    artifact.

    Signature:


    interface ArtifactRequest {
        id: string
    }


    type IPAddress = string

    type MACAddress = string

    type Timestamp = string

    interface UserProfile {
        ip_address : IPAddress,
        mac_address : MACAddress,
    }

    interface Tag {
        label: string,
        user_profile: UserProfile,
    }

    interface Annotation {
        timestamp: Timestamp,
        description:  string,
        user_profile: UserProfile
    }

    interface Artifact {
        user_profile: UserProfile,
        timestamp: Timestamp,
        tags: List<Tag>,
        type: string,
        id: string,
    }

    interface Keystroke  {
        artifact: Artifact,
        key_press: string,
    }

    interface MouseAction {
        artifact: Artifact,
        button: string,
        mouse_action:  string,
        mouse_action_value: string,
        active_window:  string,
        window_focus: string,
        process: string,
    }


    interface Screenshot {
        artifact: Artifact,
        screenshot_name: string,
        screenshot_file: string,
        screenshot_size: string,
        screenshot_format: string,
    }


    interface WindowHistory {
        artifact: Artifact,
        primary_screen_resolution: string,
        window_position: string,
        visible: string,
        window_placement_command: string,
        minimized: string,
        maximized: string,
        application_name: string,
        window_style: string,
        window_title: string,
        window_creation_time: string,
        window_destruction_time: string,
        window_id: string,
    }


    interface Process {
        artifact: Artifact,
        user_name: string,
        process_name: string,
        process_id: string,
        parent_process_id: string,
        start_time: string,
        command: string,
        terminal: string,
        status: string,
        memory_usage: string,
        no_of_threads: string,
        cpu_percentage: string,
        process_privileges: string,
        process_priority: string,
        process_type: string,
    }


    interface SystemCall {
        artifact: Artifact,
        systemcall_name: string,
        systemcall_args: string,
    }

    interface NetworkActivity {
        artifact: Artifact,
        PCAPFile: string,
        start_time: string,
        end_time: string,
        summary: string,
    }

    interface Video {
        artifact: Artifact,
        video_file_link: string,
        video_name: string,
        video_size: string,
        video_resolution: string,
        video_frame_rate: string,
        video_duration: string,
    }


    type ArtifactResponse = union {
        Keystroke(Keystroke),
        MouseAction(MouseAction),
        Screenshot(Screenshot),
        WindowHistory(WindowHistory),
        Process(Process),
        SystemCall(SystemCall),
        NetworkActivity(NetworkActivity),
        Video(Video),
    }


    ArtifactResponse post_artifact(ArtifactRequest request)

    Author: David Morales

    Preconditions:
    @requires request['id'] is contained in artifacts
    @requires request['id'] be a valid id in hexadecimal format


    Postconditions:
    @ensures \exists int i; i >= 0 && i < artifacts.length; artifacts[i]['id']  == request['id'] ==> \result == artifacts[i]
    """
    artifact_id = request.get_json()['id']
    response = jsonify(get_artifact(artifact_id))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/all_ip_addresses', methods=['POST'])
def post_all_ip_addresses():  # A request to get all IP Addresses from the DB
    """
    Returns a list of all the ip addresses that are recorded in the system.

    Signature: List<string> post_get_all_ip_addresses()

    Author: Jose Rodriguez

    Preconditions:
    @requires artifacts.length != 0

    Postconditions:
    @ensures \forall int i; i >= 0 && i < \results.length; (\exists int j; j >= 0 && j < artifacts.length; artifacts[j].artifact.user_profile.ip_address == \results[i])
    @ensures \forall int i; i >= 0 && i < artifacts.length; (\exists int j; j >= 0 && j < \results.length; artifacts[i].artifact.user_profile.ip_address == \results[j])
    """
    response = jsonify(get_all_ip_addresses())
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/all_mac_addresses', methods=['POST'])
def post_all_mac_addresses():  # A request to get all MAC Addresses from the DB
    """
    Returns a list of all the mac addresses that are recorded in the system.

    Signature: List<string> post_get_all_mac_addresses()

    Author: Jose Rodriguez

    Preconditions:
    @requires artifacts.length != 0

    Postconditions:
    @ensures \forall int i; i >= 0 && i < \results.length; (\exists int j; j >= 0 && j < artifacts.length; artifacts[j].artifact.user_profile.mac_address == \results[i])
    @ensures \forall int i; i >= 0 && i < artifacts.length; (\exists int j; j >= 0 && j < \results.length; artifacts[i].artifact.user_profile.mac_address == \results[j])
    """
    response = jsonify(get_all_mac_addresses())
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/all_tags', methods=['POST'])
def post_all_tags():  # A request to get all tags from the DB
    """
    Returns a list of all the tags that are recorded in the system.

    Signature: List<string> post_get_all_tags()

    Author: Jose Rodriguez

    Preconditions:
    @requires artifacts.length != 0

    Postconditions:
    @ensures \forall int i; i >= 0 && i < \results.length; (\exists int j; j >= 0 && j < artifacts.length; artifacts[j].artifact.tags ∈ \results[i])
    @ensures \forall int i; i >= 0 && i < artifacts.length; (\forall int k; k >= 0 && k < artifacts[i].artifact.tags.length; (\exists int j; j >= 0 && j < \results.length; artifacts[i].artifact.tags[k] == \results[j]))
    """
    response = jsonify(get_all_tags())
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


settings = {'mouse_actions': True, 'keystrokes': False}


@app.route('/recording_settings', methods=['POST'])
def post_recording_settings():
    """
    The purpose of this function is to return the current recording status of
    all artifact types.

    Signature:

    interface Configuration {
        keystrokes: boolean,
        mouse_actions: boolean,
        screenshot: boolean,
        process: boolean,
        window_history: boolean,
        system_call: boolean,
        video: boolean,
        network_activity: boolean
    }

    Configuration post_recording_settings()


    Author: David Morales


    Preconditions:
    @requires current_configuration != null


    Postconditions:
    @ensures \result['keystrokes'] ==> keystrokes are recorded from startup
    @ensures \result['mouse_actions'] ==> mouse actions are recorded from startup
    @ensures \result['screenshot'] ==> screenshot are recorded from startup
    @ensures \result['process'] ==> process are recorded from startup
    @ensures \result['window_history'] ==> window history are recorded from startup
    @ensures \result['system_call'] ==> system calls are recorded from startup
    @ensures \result['video'] ==> video are recorded from startup
    @ensures \result['network_activity'] ==> network activity are recorded from startup
    """
    response = jsonify(recording_settings())
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/update_recording_settings', methods=['POST'])
def post_update_recording_settings():
    """
    Updates the default recording configuration for different items.

    Signature:

    interface Configuration {
        keystrokes: boolean,
        mouse_actions: boolean,
        screenshot: boolean,
        process: boolean,
        window_history: boolean,
        system_call: boolean,
        video: boolean,
        network_activity: boolean
    }

    void post_update_recording_settings(Configuration configuration)

    Author: David Morales

    Preconditions:
    @requires configuration != null


    Postconditions:
    @ensures configuration['keystrokes'] ==> keystrokes are recorded from startup
    @ensures configuration['mouse_actions'] ==> mouse actions are recorded from startup
    @ensures configuration['screenshot'] ==> screenshot are recorded from startup
    @ensures configuration['process'] ==> process are recorded from startup
    @ensures configuration['window_history'] ==> window history are recorded from startup
    @ensures configuration['system_call'] ==> system calls are recorded from startup
    @ensures configuration['video'] ==> video are recorded from startup
    @ensures configuration['network_activity'] ==> network activity are recorded from startup
    """
    global settings
    settings = request.get_json()
    response = jsonify(update_recording_settings(settings))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/annotate', methods=['POST'])
def post_annotation():  # Contains routing information to add an annotation.
    """
    Adds a new annotation for a given artifact.

    Signature:

    interface AnnotationRequest {
        text: string,
        artifact_id: string,
    }

    interface AnnotationResponse {
        ip_address: string,
        mac_address: string,
        text: string,
        timestamp: string,
    }

    AnnotationResponse post_annotation(AnnotationRequest request)

    Author: David Morales

    Preconditions:
    @requires artifacts[request.artifact_id] != null

    Postconditions:
    @ensures artifacts[request.artifact_id].artifact.annotations.length = \old(artifacts[request.artifact_id].artifact.annotations.length) + 1
    @ensures artifacts[request.artifact_id].artifact.annotations[-1].text = request.text
    @ensures \forall int i; i >= 0  && i < artifacts[request.artifact_id].artifact.annotations.length - 1; artifacts[request.artifact_id].artifact.annotations[i] == \old(artifacts[request.artifact_id].artifact.annotations[i])
    """
    # Gets artifact ID and annotation content from GUI
    print(request.get_json())
    # The new annotation is needed to be returned in the response.
    response = jsonify(annotate(request.get_json()))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/new_tag', methods=['POST'])
def post_new_tag():  # Contains routing information to add a tag.
    """
    Adds a new tag for a given artifact.

    Signature:

    interface TagRequest {
        text: string,
        artifact_id: string,
    }

    interface TagResponse {
        ip_address: string,
        mac_address: string,
        text: string,
        timestamp: string,
    }

    TagResponse post_new_tag(TagRequest request)

    Author: David Morales

    Preconditions:
    @requires artifacts[request.artifact_id] != null

    Postconditions:
    @ensures artifacts[request.artifact_id].artifact.tags.length = \old(artifacts[request.artifact_id].artifact.tags.length) + 1
    @ensures artifacts[request.artifact_id].artifact.tags[-1].text = request.text
    @ensures \forall int i; i >= 0  && i < artifacts[request.artifact_id].artifact.tags.length - 1; artifacts[request.artifact_id].artifact.tags[i] == \old(artifacts[request.artifact_id].artifact.tags[i])
    """
    print(request.get_json())  # Gets artifact ID and tag content from GUI
    # The new tag is needed to be returned in the response.
    response = jsonify(new_tag(request.get_json()))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/delete_tags', methods=['POST'])
def post_delete_tags():  # Contains routing information to delete a tag.
    """
    Deletes a tag from an artifact in the system.

    Signature:

    interface DeleteTagsRequest {
        artifact_id: string,
        tags: List<string>,
    }

    void post_delete_tags(DeleteTagsRequest request)

    Author: David Morales

    Preconditions:
    @requires artifacts[request.artifact_id] != null
    @requires \forall int i; i >= 0 && i < request.tags.length; request.tags[i] ∈ artifacts[request.artifact_id].artifact.tags 

    Postconditions:
    @ensures \forall int i; i >= 0 && i < request.tags.length; !(request.tags[i] ∈ artifacts[request.artifact_id].artifact.tags)
    @ensures \forall int i; i >= 0 && i < \old(artifacts[request.artifact_id].tags.length); \old(artifacts[request.artifact_id].tags[i]) ∈ artifacts[request.artifact_id].tags <==>  \old(artifacts[request.artifact_id].tags[i]) ∈ request.tags &&    \old(artifacts[request.artifact_id].tags[i]) ∈ \old(artifacts[request.artifact_id].tags)
    """
    print(request.get_json())
    # Nothing needed on the reponse.
    response = jsonify(delete_tags(request.get_json()))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/take_screenshot', methods=['POST'])
def post_take_screenshot():  # Contains routing information to take a screenshot
    """
    Takes a screenshot of the current screen.

    Signature:
    void post_take_screenshot()

    Author: Jose Rodriguez

    Precondition:
    @requires computer to have a display (not headless).

    Postcondition:
    @ensures artifacts.length == \old(artifacts.length) + 1
    @ensures artifacts[artifacts.length - 1].type == "screenshot"
    """
    print('Taking a screenshot!')
    take_screenshot()
    print('Screenshot taken!')
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/delete_ids', methods=['POST'])
def post_delete_ids():  # Contains routing information to take a screenshot
    """
    Deletes artifact ids from the system.

    Signature:

    void  post_delete_ids(List<string> ids)

    Author: Jose Rodriguez

    Preconditions:
    @requires \forall int i; i >= 0 && i < ids.length; artifacts[ids[i]] != null

    Postconditions:
    @ensures artifacts.length <= \old(artifacts.length)
    @ensures \forall int i; i >= 0 && i < \old(artifacts.length); artifacts[i] != null <==> (\exists int i; i >= 0 && i < ids.length; ids[i] == i)
    """
    print('Deleting ids')
    delete_ids(request.get_json()['ids'])
    print('Ids deleted.')
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# Request will look like this:
# The order in which the ids appear is the order in which the steps will
# execute.
# wait_time is the amount of time to wait between actions in seconds.
# {artifact_ids: ["1241242", "41242"], wait_time: 0.05}
@app.route('/generate_script', methods=['POST'])
def post_generate_script():  # Contains routing information to take a screenshot
    """
    This function generates a script from the selected artifacts with a wait
    time.


    Signature:

    interface ScriptRequest {
        artifact_ids: List<string>,
        wait_time: float,
    }

    interface ScriptResponse {
        script: string
    }


    ScriptResponse post_generate_script(ScriptRequest request)


    Author: Timothy McCrary


    Preconditions (semi-formal since it's quite subjective):
    @requires \forall int i; i >= 0 && i < request.artifact_ids.length; artifacts[request.artifact_ids[i]] != null

    Postconditions:
    @ensures \result.script contains a python string that executes the commands in request.artifact_ids
    @ensures interval between actions == request.wait_time
    """
    print('Received request: ', request.get_json())
    print('Generating script')
    ids = request.get_json()['artifact_ids']
    wait_time = request.get_json()['wait_time']

    script_string = ScriptHandler.generate_script(ids, wait_time, None)

    response = jsonify({'script': script_string})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/get_pcap', methods=['POST'])
def post_get_pcap():  # Contains routing information to take a screenshot
    """
    Returns the raw pcap data for a given artifact id.

    Signature:

    interface PcapRequest {
        id: string,
    }

    interface PcapResponse {
        content: string,
    }

    PcapResponse post_get_pcap(PcapRequest request)

    Author: Jose Rodriguez


    Preconditions (Semiformat since subjective):
    @requires artifacts[request.id] != null
    @requires artifacts[request.id].artifact.type == "network_activity"


    Postconditions:
    @ensures \results.content is a valid wireshark pcap capture file in base64 format.
    @ensures \results.content represents the packets in artifacts[request.id]
    """
    response = get_pcap(request.get_json()['id'])
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/start_screen_recording', methods=['GET', 'POST'])
def post_start_screen_recording():  # Contains routing information to take a start screen recording
    """
    Starts screen recording.

    Signature: void post_start_screen_recording()

    Author: Timothy McCrary

    Preconditions (semiformal):
    @requires Current machine needs to have the ability to record screen.
    @requires Screen to not  currently be recording.

    Postconditions:
    @ensures screen recording has started.
    """
    VideoRecordingHandler.start()
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Route to stop screen recording


@app.route('/stop_screen_recording', methods=['GET', 'POST'])
def post_stop_screen_recording():  # Contains routing information to take a start screen recording
    """
    Stops screen recording.

    Signature: void post_stop_screen_recording()

    Author: Timothy McCrary

    Preconditions (semiformal):
    @requires Current machine needs to have the ability to record screen.
    @requires Screen is currently recording.

    Postconditions:
    @ensures screen recording has stopped.
    @ensures \artifacts.length == \old(artifacts.length) + 1
    @ensures \artifacts[-1].type == 'video'
    """
    print("Stopping screen recording")
    VideoRecordingHandler.stop()
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route("/is_screen_recording", methods=['GET', 'POST'])
def post_is_screen_recording():
    """
    Returns whether or not machine is currently recording:

    Signature:

    interface IsRecordingResponse  {
        isScreenRecording: boolean
    }

    IsRecordingResponse post_is_screen_recording()

    Author: Timothy McCrary

    Preconditions:
    @requires analyst machine able to record screen (!headless)


    Postconditions:
    @ensures \result.isScreenRecording <==> Analyst's screen is currently being
    recorded.
    """
    response = jsonify(
        {'isScreenRecording': VideoRecordingHandler.is_screen_recording()})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


"""


Sync pseudocode(sync status text and numbers are updated during each):

    1. / start_sync is called with the target id and a new sync thread
       responsible for the next steps is created.
    2. Get all ids from target.
    3. Get all local ids.
    4. Compare and find out which ids are needed.
    5. Request x artifacts at a time until all artifacts are exchanged and
       save into mongodb.
    6. If artifact requires a file(screenshot, pcap, video, etc...) a separate
       endpoint is used to transfer the file.
"""

"""
Returns the needed information for bar and pie charts


The request is the same as the one given to searching for a query.

The response is a dictionary containing the counts of the information to be
counted.


{
 "processes": 13,
 "x": 234
}
"""


@app.route('/proportional_visualization', methods=['POST'])
def post_proportional_visualization():
    """
    Returns the needed information to generate pie charts and bar charts.

    Signature:

    (The query is the same query that is used for the search endpoint)

    Map<string, int> proportional_visualization(Query query)

    Author: Jose Rodriguez

    Precondition:
    @requires query is a valid formed query

    Postconditions:
    @ensures \forall key: \result; result[key] >= 0
    @entures \result.length > 0
    """
    response = jsonify(generate_proportional_visualization(request.get_json()))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/timeline_visualization', methods=['POST'])
def post_timeline_visualization():
    """
    Returns the needed information for generating timeline visualizations.

    Signature:

    interface Summary {
        summary: string,
        x: float,
        y: float,
    }

    (The query is the same query that is used for the search endpoint)

    Map<String, List<Summary>>  post_timeline_visualization(Query query)

    Author: Jose Rodriguez

    Preconditions:
    @requires query is a valid formed query.


    Postconditions:
    @entures \forall key: \result; result[key].length >= 0
    @entures \result.length > 0
    """
    response = jsonify(generate_timeline_visualization(request.get_json()))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/get_sync_status', methods=['POST'])
def post_get_sync_status():
    """
    Returns the current sync status:

    Signature:

    interface Status {
        keystroke_total_count: int,
        mouse_action_total_count: int,
        screenshot_total_count: int,
        process_total_count: int,
        window_history_total_count: int,
        system_call_total_count: int,
        video_total_count: int,
        network_activity_total_count: int,
        artifact_total_count: int,
        keystroke_counter: int,
        mouse_action_counter: int,
        screenshot_counter: int,
        process_counter: int,
        window_history_counter: int,
        system_call_counter: int,
        video_counter: int,
        network_activity_counter: int,
        artifact_counter: int,
        total_storage: float,
        used_storage: float,
        free_storage: float
    }

    Status post_get_sync_status()

    Author: David Morales

    Preconditions:
    @requires application must be currently undergoing a sync.


    Postconditions:
    @ensures \result['keystroke_total_count'] is the count for keystroke_total_count
    @ensures \result['mouse_action_total_count'] is the count for mouse_action_total_count
    @ensures \result['screenshot_total_count'] is the count for screenshot_total_count
    @ensures \result['process_total_count'] is the count for process_total_count
    @ensures \result['window_history_total_count'] is the count for window_history_total_count
    @ensures \result['system_call_total_count'] is the count for system_call_total_count
    @ensures \result['video_total_count'] is the count for video_total_count
    @ensures \result['network_activity_total_count'] is the count for network_activity_total_count
    @ensures \result['artifact_total_count'] is the count for artifact_total_count
    @ensures \result['keystroke_counter'] is the count for keystroke_counter
    @ensures \result['mouse_action_counter'] is the count for mouse_action_counter
    @ensures \result['screenshot_counter'] is the count for screenshot_counter
    @ensures \result['process_counter'] is the count for process_counter
    @ensures \result['window_history_counter'] is the count for window_history_counter
    @ensures \result['system_call_counter'] is the count for system_call_counter
    @ensures \result['video_counter'] is the count for video_counter
    @ensures \result['network_activity_counter'] is the count for network_activity_counter
    @ensures \result['artifact_counter'] is the count for artifact_counter
    @ensures \result['total_storage'] is the how much storage exists.
    @ensures \result['used_storage'] is how much storage exists.
    @ensures \result['free_storage'] is how much storage remains free.
    """
    response = get_sync_status()
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/get_all_artifact_ids', methods=['POST'])
def post_get_all_artifact_ids():
    """
    Returns all the artifact ids in the database of the current machine.

    Signature:
    interface Ids {
        "ids": ["321jhgkj321gh231", "dsajkdhasl"]
    }


    Ids post_get_all_artifact_ids(String target)


    Author: David Morales


    Preconditions:
    @requires target to be a valid ip that has an AVERT server running.

    Postconditions:
    @ensures \forall int i; i >= 0 && i < \result.length; \result[i] is contained inside of the target machine.
    """
    response = get_all_artifact_ids()
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/get_file', methods=['POST'])
def post_get_file():
    """
    Returns the saved files from filesystem with a given id.

    Signature:

    interface Request {"file": string}

    interface Response {"file": bytes}

    Response post_get_file(Request request)

    AUthor: David Morales

    Preconditions:
    @requires request.file be  an existing filename in the target's  machine.

    Postconditions:
    @ensures \result.filie contains the file in a base64 bytes format.
    """
    response = get_file(request.get_json())
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/get_artifact_to_sync', methods=['POST'])
def post_get_artifact_to_sync():
    """
    Returns the artifact data in a JSON format

    Request: {"ids": ["1o321o83721", "12312415", "hjksadkhsad"]}

    Response:

    {"artifacts":
        [
            {"id": "asdjhgasdjkg", "object": {"_id": ...},
                "extra": [{"type": "video", "id": "1283712986"}]},
            {"id": "asdjhgasdjkg", "object": {"_id": ...},
                "extra": [{"type": "pcap", "id": "caskjdhalsk"}]},
            {"id": "asdjhgasdjkg", "object": {
                "_id": ..., "type": "keystroke"}, "extra": []},
        ]}


    Signature:
    List<Map<String, ?>>  post_get_artifact_to_sync(List<String> ids)


    Author: David Morales

    Preconditions:
    @requires \forall int i; i >= 0 && i < ids.length; artifacts[ids[i]] != null

    Postconditions:
    @ensures \forall int i; i >= 0 && i < ids.length; \results[i] == artifacts[i]
    @ensures \result.length == ids.length
    """
    response = {}
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/receive_artifact_from_sync', methods=['POST'])
def post_receive_artifact_from_sync():
    """
    Given an artifact, stores the artifact  into the local avert system.

    Signature:
    void post_receive_artifact_from_sync(Map<string, ?> artifact)

    Author: David Morales

    Preconditions:
    @requires artifact.type ∈ ["screenshot", "process", "system_call", "window_history", "keystroke", "mouse_action", "video", "network_activity"]

    Postconditions:
    @ensures artifact is now saved into the local database
    @ensures artifacts.length == \old(artifacts.length) + 1
    @ensures artifacts[-1] == artifact
    """
    artifacts = request.get_json()
    print(artifacts)
    ip_addr = request.remote_addr
    response = receive_artifact_from_sync(artifacts, ip_addr)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/cancel_sync', methods=['POST'])
def post_cancel_sync():
    """
    Cancels a sync by updating the sync status.


    Signature:

    interface Request {
        keystroke: boolean,
        mouse_action: boolean,
        screenshot: boolean,
        process: boolean,
        window_history: boolean,
        system_call: boolean,
        video: boolean,
        network_activity: boolean,
    }

    void post_cancel_sync(Request request)

    Author: David Morales

    Preconditions:
    @requires request != null    

    Postconditions:
    @ensures \result['keystroke'] <==> keystrokes are synced
    @ensures \result['mouse_actions'] <==> mouse actions are synced
    @ensures \result['screenshot'] <==> screenshots are synced
    @ensures \result['process'] <==> processes are synced
    @ensures \result['window_history'] <==> window history are synced
    @ensures \result['system_call'] <==> system calls are synced
    @ensures \result['video'] <==> videos are synced
    @ensures \result['network_activity'] <==> network activity artifacts are synced
    """
    active = request.get_json()
    response = cancel_sync(active)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/start_sync', methods=['POST'])
def post_get_start_sync():
    """
    Triggers the starting of a sync that makes the current machine request
    sync the information of the "target" machine into itself.

    interface Request {"target": "192.1.12.72", artifacts_to_sync = {
    'keystroke': True,
    'mouse_action': True,
    'screenshot': True,
    'process': True,
    'window_history': True,
    'system_call': True,
    'video': True,
    'network_activity': True
    }

    Response: void

    Response post_get_start_sync(Request request)

    Author: David Morales

    Preconditions:
    @requires request.target != null
    @requires request.artifacts_to_sync to be well formed.
    @requires request.target to be  a valid ip address that has an avert api
    instance running.


    Postconditions:
    @ensures after the  request is commenced, syncing will commence.
    """

    start_sync(request.get_json())
    response = {}
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def main():
    """
    Commences recording of required artifacts and commences  serving  of requests.


    Siganture:

    void main()

    Author: David Morales, Jose Rodriguez


    Preconditions:
    @requires port 5000 is available
    @requires mongodb instance is running on port 27017  
    @requires recording configuration is loaded.



    Postconditions:
    @ensures serving of requests as they come in http protocol.
    @ensures recording of artifacts until the program  stops running.
    """

    client = MongoClient(port=27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)
    dbs = database.DatabaseService(client, db, fs)

    types_to_record = dbs.configuration_db_get()  # Gets configuration from database

    # Checks dict to see if artifact type is true
    if types_to_record.get("keystrokes"):
        KeyLogger.start()
    if types_to_record.get("mouse_actions"):
        # Forks into a process so we can run different kinds of loggers.
        thread = threading.Thread(target=MouseLogger.start)
        thread.start()
    if types_to_record.get("screenshot"):
        print('Starting screenshot printing!')

        ScreenshotKeyLogger.start()

        pid = os.fork()
        if pid == 0:
            ScreenshotMouseListener.start()
            exit()

    if types_to_record.get("process"):
        thread = threading.Thread(target=Processes.start)
        thread.start()

    if types_to_record.get("window_history"):
        thread = threading.Thread(target=WindowHistory.start)
        thread.start()

    if types_to_record.get("system_call"):
        thread = threading.Thread(target=CommandHistory.start)
        thread.start()

    if types_to_record.get("video"):
        # VideoRecordingHandler.start()
        # thread = threading.Thread(target=VideoRecordingHandler.start)
        VideoRecordingHandler.start()

    if types_to_record.get("network_activity"):
        thread = Thread(
            target=continuously_record_network_activity, args=(20,))
        thread.start()

    app.run(host="0.0.0.0", port=5000)


if __name__ == '__main__':
    main()
