import pyshark
import uuid
import os

from artifacts.user_profile_artifact import UserProfileArtifact
from artifacts.meta_data_helper import MetaDataHelper

import database
from pymongo import MongoClient
import gridfs
from database import DatabaseService
import time
import subprocess


'''/*
Purpose:The purpose of this method is to add the path where the packet file  is stored.
Author: Jose Rodriguez 
Pre-Condition:@requires AVERT to be working.
              @requires AVERT to be connected to the database.

Post-Condition:@ensures the filename path is returned as a string
*/'''

def add_path(filename):
    return "./pcap/" + filename

'''/*
Purpose:The purpose of this method is to add the absolute path where the packet file  is stored.
Author: Jose Rodriguez 
Pre-Condition:@requires AVERT to be working.
              @requires AVERT to be connected to the database.

Post-Condition:@ensures the filename absolute path is returned as a string
*/'''

def add_absolute_path(filename):
    filename_with_path = add_path(filename)
    return os.path.abspath(filename_with_path)

'''/*
Purpose:The purpose of this method is to provide a summary of the packets similar to how it is previewed within wireshark
Author: Jose Rodriguez 
Pre-Condition:@requires AVERT to be working.
              @requires AVERT to be connected to the database.

Post-Condition:@ensures the summary returned as a string
*/'''

def create_summary(filename):
    absolute_path = add_absolute_path(filename)
    cap = pyshark.FileCapture(absolute_path, only_summaries=True)
    out = set()
    for packet in cap:
        out.add(repr(packet).replace('<PacketSummary ', '').replace('>', ''))
    if len(out) == 0:
        return 'no packets during this time period.'
    return '|'.join(out)
'''/*
Purpose:The purpose of this method is to record network activity within the system for the given number of seconds
Author: Jose Rodriguez 
Pre-Condition:@requires AVERT to be working.
              @requires AVERT to be connected to the database.
              @requires filepath to the pcap packets
              @requires start time 
              @requires end time

Post-Condition:@ensures the network activcity is stored into the database
               
*/'''

def record_network_activity(seconds):
    filename = str(uuid.uuid1()) + ".pcap"
    absolute_path = add_absolute_path(filename)

    user_profile = UserProfileArtifact()
    tags = []
    annotation = []
    start_time = MetaDataHelper.get_zulu_time()

    # Needed in order to be able to record as a super user.
    os.system(f'touch {absolute_path}')
    os.system(f'chmod o=rw {absolute_path}')

    command = f'tshark -w {absolute_path} -a duration:{seconds}'
    print('Running: ' + command)

    result = os.system(command)

    end_time = MetaDataHelper.get_zulu_time()
    if result == 0:
        print(f'Saved network activity: {filename}')
        summary = create_summary(filename)

        client = MongoClient(port=27017)
        db = client.AVERT
        fs = gridfs.GridFS(db)
        database = DatabaseService(client, db, fs)

        database.network_activity_db_write(
            filename, start_time, end_time, user_profile.__dict__, tags, annotation, summary)
        print('Network activity recorded!')
    else:
        print('Error recording network activity!')

'''/*
Purpose:The purpose of this method is to add the path where the packet file  is stored.
Author: Jose Rodriguez 
Pre-Condition:@requires AVERT to be working.
              @requires AVERT to be connected to the database.
              @requires filepath to the pcap packets



Post-Condition:@ensures the network activcity is stored into the database
*/'''

def continuously_record_network_activity(seconds):
    while True:
        print('Executing!')
        record_network_activity(seconds)
        time.sleep(1)


def main():
    record_network_activity(5)
    print('End of tranmission. Don\'t panic!')


if __name__ == '__main__':
    main()
