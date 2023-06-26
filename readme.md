# AVERT API

Http flask api used by Team 3's AVERT implementation.

## Installation

In order to install, intall the following pip dependencies:

```sh
pip3 install flask flask_cors
```

## Running

Run python3 main.py in order to run the server.

## Endpoints

The API has the following endpoints:

### /search

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


        ### /search
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

### /artifact

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

### /all_ip_addresses

    Returns a list of all the ip addresses that are recorded in the system.

    Signature: List<string> post_get_all_ip_addresses()

    Author: Jose Rodriguez

    Preconditions:
    @requires artifacts.length != 0

    Postconditions:
    @ensures \forall int i; i >= 0 && i < \results.length; (\exists int j; j >= 0 && j < artifacts.length; artifacts[j].artifact.user_profile.ip_address == \results[i])
    @ensures \forall int i; i >= 0 && i < artifacts.length; (\exists int j; j >= 0 && j < \results.length; artifacts[i].artifact.user_profile.ip_address == \results[j])

### /all_mac_addresses

    Returns a list of all the mac addresses that are recorded in the system.

    Signature: List<string> post_get_all_mac_addresses()

    Author: Jose Rodriguez

    Preconditions:
    @requires artifacts.length != 0

    Postconditions:
    @ensures \forall int i; i >= 0 && i < \results.length; (\exists int j; j >= 0 && j < artifacts.length; artifacts[j].artifact.user_profile.mac_address == \results[i])
    @ensures \forall int i; i >= 0 && i < artifacts.length; (\exists int j; j >= 0 && j < \results.length; artifacts[i].artifact.user_profile.mac_address == \results[j])

### /all_tags

    Returns a list of all the tags that are recorded in the system.

    Signature: List<string> post_get_all_tags()

    Author: Jose Rodriguez

    Preconditions:
    @requires artifacts.length != 0

    Postconditions:
    @ensures \forall int i; i >= 0 && i < \results.length; (\exists int j; j >= 0 && j < artifacts.length; artifacts[j].artifact.tags ∈ \results[i])
    @ensures \forall int i; i >= 0 && i < artifacts.length; (\forall int k; k >= 0 && k < artifacts[i].artifact.tags.length; (\exists int j; j >= 0 && j < \results.length; artifacts[i].artifact.tags[k] == \results[j]))

### /recording_settings

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

### /update_recording_settings

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

### /annotate

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

### /new_tag

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

### /delete_tags

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

### /take_screenshot

    Takes a screenshot of the current screen.

    Signature:
    void post_take_screenshot()

    Author: Jose Rodriguez

    Precondition:
    @requires computer to have a display (not headless).

    Postcondition:
    @ensures artifacts.length == \old(artifacts.length) + 1
    @ensures artifacts[artifacts.length - 1].type == "screenshot"

### /delete_ids

    Deletes artifact ids from the system.

    Signature:

    void  post_delete_ids(List<string> ids)

    Author: Jose Rodriguez

    Preconditions:
    @requires \forall int i; i >= 0 && i < ids.length; artifacts[ids[i]] != null

    Postconditions:
    @ensures artifacts.length <= \old(artifacts.length)
    @ensures \forall int i; i >= 0 && i < \old(artifacts.length); artifacts[i] != null <==> (\exists int i; i >= 0 && i < ids.length; ids[i] == i)

### /generate_script

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

### /get_pcap

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

### /start_screen_recording

    Starts screen recording.

    Signature: void post_start_screen_recording()

    Author: Timothy McCrary

    Preconditions (semiformal):
    @requires Current machine needs to have the ability to record screen.
    @requires Screen to not  currently be recording.

    Postconditions:
    @ensures screen recording has started.

### /stop_screen_recording

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

### /is_screen_recording

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

### /proportional_visualization

    Returns the needed information to generate pie charts and bar charts.

    Signature:

    (The query is the same query that is used for the search endpoint)

    Map<string, int> proportional_visualization(Query query)

    Author: Jose Rodriguez

    Precondition:
    @requires query is a valid formed query

    Postconditions:
    @ensures \forall key: \result; result[key] >= 0
    @ensures \result.length > 0

### /timeline_visualization

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
    @ensures \forall key: \result; result[key].length >= 0
    @ensures \result.length > 0

### /get_sync_status

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

### /get_all_artifact_ids

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

### /get_file

    Returns the saved files from filesystem with a given id.

    Signature:

    interface Request {"file": string}

    interface Response {"file": bytes}

    Response post_get_file(Request request)

    Author: David Morales

    Preconditions:
    @requires request.file be  an existing filename in the target's  machine.

    Postconditions:
    @ensures \result.filie contains the file in a base64 bytes format.

### /get_artifact_to_sync

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

### /receive_artifact_from_sync

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

### /cancel_sync

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

### /start_sync

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
