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
from screenshot_taker import take_screenshot


class ScreenshotKeyLogger:
    """ Handles keystroke logging.
    """

    __hook: HookManager

    @staticmethod
    def start():
        """ Starts the key logging.
        """
        ScreenshotKeyLogger.__log_keys()

    @staticmethod
    def __on_key_press_callback(event: PyxHookKeyEvent) -> None:
        if event.Key in ['Tab', 'Return', 'Escape']:
            print('Taking screenshot!')
            take_screenshot()
            print('Screenshot taken!')

    @staticmethod
    def __log_keys() -> None:
        """ Starts logging keystrokes using pyxhook.
        """
        # create a hook manager object
        ScreenshotKeyLogger.__hook = pyxhook.HookManager()
        # new_hook = pyxhook.HookManager()
        ScreenshotKeyLogger.__hook.KeyDown = ScreenshotKeyLogger.__on_key_press_callback

        ScreenshotKeyLogger.__hook.HookKeyboard()  # set the hook

        try:
            ScreenshotKeyLogger.__hook.start()  # start the hook
        except KeyboardInterrupt:
            # User cancelled from command line.
            pass
        except Exception as ex:
            # Write exceptions to the log file, for analysis later.
            msg = f"Error while catching events:\n  {ex}"
            pyxhook.print_err(msg)
