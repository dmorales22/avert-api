from pymongo import MongoClient
import database
import gridfs
import datetime
from pprint import pprint

client = MongoClient(port = 27017)
db = client.AVERT
fs = gridfs.GridFS(db)
database = database.DatabaseService(client, db, fs)

userprofile_example = {
    "ip_address": "192.168.1.159",
    "mac_address": "33:FF:FF:FF:FF"
    }

tags_example = [{"label": "lol", "user_profile": userprofile_example}]

start = datetime.datetime(2020, 8, 20, 7, 51, 4)
test_date = datetime.datetime(2021, 9, 20, 7, 12)
end = datetime.datetime(2022, 10, 21, 7, 52, 4)

annotation_example = [{
    "timestamp": test_date,
    "description": 'This is test keystroke.',
    "user_profile": userprofile_example
}]

query = {'types': {'stillScreenshot': False, 'video': False, 'networkPacket': False, 'process': False, 'keystroke': True, 'mouseAction': False, 'windowHistory': False, 'systemCall': False, 'history': False, 'log' : True, 'all': False, 'allArtifactsTypes': False}, 'ip_addresses': [], 'mac_addresses': [], 'time_range': [], 'expression': 'd', 'selected_tags': []}

#database.keystroke_db_write('t', test_date, userprofile_example, tags_example, annotation_example)
#database.mouse_action_db_write("Left Button", "Click", "bitmap", "Terminal", "AVERT", "AVERT", test_date, userprofile_example, tags_example, annotation_example)
#database.annotation_db_write("615c15dfc730b68bdd80abef", annotation_example)
#database.tags_db_write("615c15dfc730b68bdd80abef", tags_example)

#database.database_delete_id("615c6f6e6d2de7d011d58a17")

#database.tags_db_delete("615cbed5bd88d07070f6dea4", ['lol'])

#image = open("100_0856.JPG", 'rb')
#database.screenshot_db_write(image, "1024x720","JPG",test_date, userprofile_example, tags_example, annotation_example)

#database.window_history_db_write("1024x720", "Top", True, "xfce", False, True, "AVERT GUI", "TrueColor", "Configuration", "2021-01-05T22:12:50.810Z", "2021-01-05T22:12:55.810Z", test_date, userprofile_example, tags_example, annotation_example)

#database.process_db_write("kali", "nmap", "1443", "1203", "2021-01-05T22:12:50.810Z", "nmap -v", "tty0", "running", "14.3 MB", "2", "13%", "root", "0", "1", test_date, userprofile_example, tags_example, annotation_example)

#database.systemcall_db_write("open()", "rb", "1", "File Management", test_date, userprofile_example, tags_example, annotation_example)

#video_file = open("nyan.mp4", 'rb')
#database.video_db_write('/home/sloshed/avert-api/videos/test.avi', "test", "12.2 MB", "480x200", "30 fps", "10 minutes 4 seconds", test_date, userprofile_example, tags_example, annotation_example)
#result = database.database_query(query)
#video_obj = result[0]
#video = fs.get(video_obj).read()
#video_write = open("test.mp4", 'wb')
#video_write.write(video)

#result_image = result[0]
#image_obj = result_image.get("screenshot_file")
#image = fs.get(image_obj).read()
#f = open("test.png", 'wb')
#f.write(image)

query = database.get_all_object_ids()
pprint(query)

#database.configuration_db_write(True, True)
#result = database.configuration_db_write(True, True)
#result = database.configuration_db_get()
#print(result)

#database.annotation_db_write(result, annotation_array, "keystroke")
