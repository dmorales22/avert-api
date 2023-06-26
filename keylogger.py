# import needed modules
import os
from datetime import datetime
import pyxhook
from pyxhook.pyxhook import HookManager, PyxHookKeyEvent
from artifacts.keystroke_artifact import KeystrokeArtifact
from artifacts.user_profile_artifact import UserProfileArtifact
from artifacts.annotation_artifact import AnnotationArticact
from database import DatabaseService
from artifacts.meta_data_helper import MetaDataHelper
import database
import gridfs
from pymongo import MongoClient

    
class KeyLogger:

    __hook: HookManager

    """
    Author: Team 3
    Purpose: This method initiates the keylogger
    @requires AVERT to be working.
    @requires AVERT to be connected to the database.
    @ensures /result A thread is spawned that writes a new keystroke         every time a keystroke occurs.
    """
    @staticmethod
    def start():
        KeyLogger.__log_keys()
        
    """
    Author: Team 3
    Purpose: Creates a key in the database with metadata to store the keystroke in the future
    @requires AVERT to be working.
    @requires AVERT to be connected to the database.
    @requires Event PyxHookKeyEvent
    @ensures /result create key document with metadata
    """
    @staticmethod
    def __on_key_press_callback(event: PyxHookKeyEvent) -> None:
        client = MongoClient(port=27017)
        db = client.AVERT
        fs = gridfs.GridFS(db)
        database = DatabaseService(client, db, fs)

        user_profile = UserProfileArtifact().__dict__

        database.add_ip(user_profile['ip_address'])
        database.add_mac(user_profile['mac_address'])

        database.keystroke_db_write(chr(event.Ascii), MetaDataHelper.get_zulu_time(
        ), UserProfileArtifact().__dict__, [], [])


    """
    Author: Team 3
    Purpose: Identifies the pressed keystroke and logs it into its specific row in the data
    @requires AVERT to be working.
    @requires AVERT to be connected to the database.
    @ensure /result Logs keystroke pressed in the database on its respective row
    """
    @staticmethod
    def __log_keys() -> None:
        """ Starts logging keystrokes using pyxhook.
        """
        # create a hook manager object
        KeyLogger.__hook = pyxhook.HookManager()
        # new_hook = pyxhook.HookManager()
        KeyLogger.__hook.KeyDown = KeyLogger.__on_key_press_callback

        KeyLogger.__hook.HookKeyboard()  # set the hook

        try:
            KeyLogger.__hook.start()  # start the hook
        except KeyboardInterrupt:
            # User cancelled from command line.
            pass
        except Exception as ex:
            # Write exceptions to the log file, for analysis later.
            msg = f"Error while catching events:\n  {ex}"
            pyxhook.print_err(msg)

