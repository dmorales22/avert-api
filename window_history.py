from artifacts.user_profile_artifact import UserProfileArtifact
from database import DatabaseService
import gridfs
from pymongo import MongoClient
from artifacts.meta_data_helper import MetaDataHelper
import subprocess
import time
from datetime import datetime, timezone

class WindowHistory:
    '''
    Author: Team 3
    Purpose: This method will start logging the window history.
    Pre-condition:  @requires AVERT to be connected to the database.
    Post-condition: @ensures \result AVERT will start logging window history information.
    '''
    @staticmethod
    def start():
        WindowHistory.log_window_history()
    
    '''
    Author: Team 3
    Purpose: This method checks if there are any new windows opened and sees what state it is in.
    Pre-condition: @requires AVERT to be connected to the database.
                   @requires windows being passed are new.
    Post-condition: @ensures \result new window information will be written into the database.
    '''
    @staticmethod
    def add_windows(added_windows, database):
        if(added_windows != None): # Checks if there are new windows
            for i in range(len(added_windows)):
                if(added_windows[i] == ""):
                    continue
                process_info = added_windows[i].split()
                window_check = database.window_history_db_query(process_info[0]) # Queries database to see if window already exists in the database
                
                if window_check != None: #If the window exits, then it skips the object
                    continue

                window_info = subprocess.Popen(["xwininfo", "-id", process_info[0]], stdout=subprocess.PIPE)
                window_info_detailed = subprocess.Popen(["xwininfo", "-all", "-id", process_info[0]], stdout=subprocess.PIPE)
                window_info_detailed_str = window_info_detailed.communicate()[0].decode("utf-8")
                window_info_list = (window_info.communicate()[0].decode("utf-8").split('\n'))

                if "Map State: IsViewable" in window_info_detailed_str: # Checks if window is visible
                    visible = True
                else: 
                    visible = False

                if "Maximized Horz" in window_info_detailed_str: # Checks if window is minimized/maximized
                    maximized = True
                    minimized = False

                else:
                    maximized = False 
                    minimized = True

                window_title = ""
                for i in range(9, len(process_info)): # Gets window title
                    window_title += process_info[i]
                
                primary_resolution = process_info[5] + "x" + process_info[6] 
                window_position = window_info_list[3] + ", " + window_info_list[4] + ", " + window_info_list[5] + ", " + window_info_list[6]
                try:
                    application_name = process_info[7].split(".")[1]
                except IndexError: 
                    application_name = process_info[7]

                process_id = process_info[0]

                database.window_history_db_write(primary_resolution, window_position, visible, "xfwm4", minimized, maximized, application_name, "", window_title, datetime.now(timezone.utc).isoformat(), "", MetaDataHelper.get_zulu_time(), UserProfileArtifact().__dict__, [], [], process_id) # Inserts window into the database
    '''
    Author: Team 3
    Purpose: This method checks to see if any windows have been closed.
    Pre-condition: @requires AVERT to be connected to the database.
                   @requires window information being passed to exist.
    Post-condition: @ensures \result removes window from database while adding in destruction time.
    '''
    @staticmethod
    def remove_windows(removed_windows, database): # Checks if windows were closed 
        if(removed_windows != None):
            for i in range(len(removed_windows)):
                if(removed_windows[i] == ""):
                    continue

                process_info = removed_windows[i].split()
                database.window_history_db_update_removed(process_info[0], datetime.now(timezone.utc).isoformat()) # Just adds the window destruction time 
    '''
    Author: Team 3
    Purpose: This method checks to see if any windows have been modified throughout its living cycle.
    Pre-condition: @requires AVERT to be connected to the database.
                   @requires window information being passed to exist.
    Post-condition: @ensures \result modifies window changes to the database.
    '''
    @staticmethod
    def update_windows(process_list, database): # Updates current windows
        for i in range(len(process_list)):
            if(process_list[i] == ""): #Skips over empty strings
                continue

            process_info = process_list[i].split()
            window_info = subprocess.Popen(["xwininfo", "-id", process_info[0]], stdout=subprocess.PIPE) 
            window_info_detailed = subprocess.Popen(["xwininfo", "-all", "-id", process_info[0]], stdout=subprocess.PIPE)
            window_info_detailed_str = window_info_detailed.communicate()[0].decode("utf-8")
            window_info_list = (window_info.communicate()[0].decode("utf-8").split('\n'))

            if "Map State: IsViewable" in window_info_detailed_str: # Checks if window is visible
                visible = True
            else: 
                visible = False

            if "Maximized Horz" in window_info_detailed_str: # Checks if window is minimized/maximized
                maximized = True
                minimized = False

            else:
                maximized = False
                minimized = True

            window_title = ""
            for i in range(9, len(process_info)):
                window_title += process_info[i]

            database.window_history_db_update(process_info[0], visible, maximized, minimized, window_title, "")

    '''
    Author: Team 3
    Purpose: This method constantly calls the other functions in the class to keep up to date on current windows.
    Pre-condition: @requires AVERT to be connected to the database.
    Post-condition: @ensures \result keeps track of whether or not new windows are created, destroyed or updated.
    '''
    @staticmethod
    def log_window_history():
        previous_list = []
        client = MongoClient(port=27017)
        db = client.AVERT
        fs = gridfs.GridFS(db)
        database = DatabaseService(client, db, fs)

        while True: #Runs loop until exited
            process = subprocess.Popen(["wmctrl", "-l", "-p", "-G", "-x"], stdout=subprocess.PIPE) #Runs the wmctrl command to get info on windows
            process_list = process.communicate()[0].decode("utf-8").split('\n') #Splits the output into a list 
            process_id_list = []
            info_list = []

            added_windows = list(set(process_list) - set(previous_list)) #Checks added windows using a set
            removed_windows = list(set(previous_list) - set(process_list)) #Checks removed (closed) windows using a set

            WindowHistory.add_windows(added_windows, database)
            WindowHistory.remove_windows(removed_windows, database)
            WindowHistory.update_windows(process_list, database)

            #print("Added:", added_windows)
            #print("Removed:", removed_windows)
            #print("Updated:", process_list)

            previous_list = process_list
            time.sleep(1.0) # Runs every second 
            
