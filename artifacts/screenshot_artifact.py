from artifacts.user_profile_artifact import UserProfileArtifact
from artifacts.meta_data_helper import MetaDataHelper
import pyautogui


class NewScreenshot:

    def __init__(self) -> None:
        self.user_profile = UserProfileArtifact()
        self.time_stamp = MetaDataHelper.get_zulu_time()
        self.tags = []
        self.annotations = []
        self.screenshot_format = "png"

        image = pyautogui.screenshot()
        image.save('temp.png')
        image_file = open('temp.png', 'rb')

        self.screenshot_file = image_file
        self.screenshot_size = str(image.size)
