from pymongo import MongoClient


def only_processes(query):
    return query['types']['process'] and not any(query['types'][key] for key in query['types'] if key != 'process')


def count_specific_to_only_processes(query):
    client = MongoClient(port=27017)
    db = client.AVERT

    before = []
    if query['expression']:
        before = [
            {"$match": {
                "process_name": {
                    "$regex": query['expression'], "$options": "i"
                }
            }}
        ]

    agg = db.Process.aggregate(
        before +
        [{"$group": {"_id": "$process_name", "sumQuantity": {"$sum": 1}}}]
    )

    return {x['_id']: x['sumQuantity'] for x in agg}


def count_screenshots(db):
    return db.Screenshot.count()


def count_video(db):
    return db.Video.count()


def count_network_activity(db):
    return db.NetworkActivity.count()


def count_processes(db):
    return db.Process.count()


def count_keystrokes(db):
    return db.Keystroke.count()


def count_mouse_actions(db):
    return db.MouseAction.count()


def count_window_history(db):
    return db.WindowHistory.count()


def count_system_call(db):
    return db.SystemCall.count()


def count_history(db):
    # TODO: Let's eventually do this when it's asked for.
    return 0


def count_log(db):
    # TODO: Let's eventually do this when it's asked for.
    return 0


type_to_count_function = {
    'stillScreenshot': count_screenshots,
    'video': count_video,
    'networkPacket': count_network_activity,
    'process': count_processes,
    'keystroke': count_keystrokes,
    'mouseAction': count_mouse_actions,
    'windowHistory': count_window_history,
    'systemCall': count_system_call,
    'history': count_history,
    'log': count_log,
}


type_to_label = {
    'stillScreenshot': 'Screenshots',
    'video': 'Videos',
    'networkPacket': 'Network Activity',
    'process': 'Processes',
    'keystroke': 'Keystrokes',
    'mouseAction': 'Mouse Actions',
    'windowHistory': 'Window History',
    'systemCall': 'System Calls',
    'history': "History",
    'log': "Logs",
}


all_types = [
    'stillScreenshot',
    'video',
    'networkPacket',
    'process',
    'keystroke',
    'mouseAction',
    'windowHistory',
    'systemCall',
    'history',
    'log',
]


all_artifact_types = [
    'stillScreenshot',
    'video',
    'networkPacket',
    'process',
    'keystroke',
    'mouseAction',
    'windowHistory',
    'systemCall',
]


def aggregate_count(types):
    client = MongoClient(port=27017)
    db = client.AVERT
    return {type_: type_to_count_function[type_](db) for type_ in types}


def find_selected_types(types):
    s = set(all_types)
    return [type_ for type_ in types if type_ in s and types[type_]]


def generate_proportional_visualization(query):
    print(query)

    # No types are selected.
    if not any(query['types'][key] for key in query['types']):
        return {'a': -1}

    if only_processes(query):
        return count_specific_to_only_processes(query)

    if query['types']['all']:
        return aggregate_count(all_types)

    if query['types']['allArtifactTypes']:
        return aggregate_count(all_artifact_types)

    return aggregate_count(find_selected_types(query['types']))
