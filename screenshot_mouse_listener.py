from mouse import ButtonEvent, WheelEvent, get_position, wait, hook
import time
from artifacts.user_profile_artifact import UserProfileArtifact
from database import DatabaseService
import gridfs
from pymongo import MongoClient
from artifacts.meta_data_helper import MetaDataHelper
from screenshot_taker import take_screenshot


class ScreenshotMouseListener:

    @staticmethod
    def start():
        ScreenshotMouseListener.__logMouse()

    @staticmethod
    def __mouseCallback(e):
        print('Taking screenshot! (Mouse click detected)')
        take_screenshot()
        print('Screenshot taken!')

    @staticmethod
    def __logMouse():
        # SETS UP THE HOOK AND EXCEPTIONS (KEYBOARD, OR UNEXPECTED ERRORS)
        try:
            # Issue keeps popping up saying hook needs to be ran from root - issue to due how boppreh was installed?
            hook(ScreenshotMouseListener.__mouseCallback)
            wait(button='none', target_types='none')
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            pass
        except Exception as ex:
            print('Mouse error found:', ex)
