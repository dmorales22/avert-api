# Imported Modules
from mouse import ButtonEvent, WheelEvent, get_position, wait, hook
import time
from artifacts.user_profile_artifact import UserProfileArtifact
from database import DatabaseService
import gridfs
from pymongo import MongoClient
from artifacts.meta_data_helper import MetaDataHelper


class MouseLogger:

    @staticmethod
    def start():
        MouseLogger.__logMouse()

    @staticmethod
    def __mouseCallback(e):
        # PRINT THE MOUSE ACTIONS and store into the mongo database
        client = MongoClient(port=27017)
        db = client.AVERT
        fs = gridfs.GridFS(db)
        database = DatabaseService(client, db, fs)

        try:
            checker = e[2]
            database.mouse_action_db_write(e[1], e[0], get_position(), [], [], [
            ], MetaDataHelper.get_zulu_time(), UserProfileArtifact().__dict__, [], [])
        except:
            database.mouse_action_db_write('wheel_scroll', e[0], get_position(), [], [], [
            ], MetaDataHelper.get_zulu_time(), UserProfileArtifact().__dict__, [], [])

    @staticmethod
    def __logMouse():
        # SETS UP THE HOOK AND EXCEPTIONS (KEYBOARD, OR UNEXPECTED ERRORS)
        try:
            # Issue keeps popping up saying hook needs to be ran from root - issue to due how boppreh was installed?
            hook(MouseLogger.__mouseCallback)
            wait(button='none', target_types='none')
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            pass
        except Exception as ex:
            print('Mouse error found:', ex)
