from datetime import datetime
import gridfs
import pyautogui
import numpy as np
import cv2
import time
import threading
import database
import os
from artifacts.meta_data_helper import MetaDataHelper
from artifacts.user_profile_artifact import UserProfileArtifact



from pymongo.mongo_client import MongoClient


class VideoRecordingHandler:

    __isRecording = False
    __file_path = ""
    __file_name = ""
    __file_size = ""
    __resolution = ""
    __fps = 0
    __duration = ""


    @staticmethod
    def start():
        if (VideoRecordingHandler.__isRecording == True):
            print("Recording already started")
            return
        print("Starting")
        VideoRecordingHandler.__isRecording = True
        threading.Thread(target=VideoRecordingHandler.__run).start()
        print("Passed video recording thread run")

    @staticmethod
    def __run():
        print("Running screen recording")
        # Create file name with current date and time
        VideoRecordingHandler.__file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".mp4"


        file_output = f'./videos/{VideoRecordingHandler.__file_name}'
        VideoRecordingHandler.__file_path = os.path.abspath(file_output)
        
        fps = 4
        VideoRecordingHandler.__fps = fps
        img = pyautogui.screenshot()
        screen_size = pyautogui.size()
        VideoRecordingHandler.__resolution = f'{screen_size[0]}x{screen_size[1]}'
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'vp09')
        out = cv2.VideoWriter(file_output, fourcc, fps, (screen_size))

        while(VideoRecordingHandler.__isRecording):

            try:
                img = pyautogui.screenshot()
                image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                out.write(image)
                StopIteration(0.5)
            except KeyboardInterrupt:
                print("Stopping screen recording from keyboard interupt")
                break
            except Exception as e:
                print("Error with screen recording")
                print(e)
                break

        out.release()
        cv2.destroyAllWindows()

    @staticmethod
    def stop():
        
        
        print("Stopping screen recording")
        VideoRecordingHandler.__isRecording = False

        client = MongoClient(port=27017)
        db = client.AVERT
        fs = gridfs.GridFS(db)
        dbs = database.DatabaseService(client, db, fs)
        # TODO: Add video recording to database

        dbs.video_db_write(VideoRecordingHandler.__file_path, VideoRecordingHandler.__file_name, VideoRecordingHandler.__file_size, VideoRecordingHandler.__resolution, VideoRecordingHandler.__fps, VideoRecordingHandler.__duration, MetaDataHelper.get_zulu_time(), UserProfileArtifact().__dict__, [], [])
        pass
    
    @staticmethod
    def is_screen_recording():
        return VideoRecordingHandler.__isRecording

if __name__ == '__main__':
    VideoRecordingHandler.start()
    print("Going to sleep")
    time.sleep(5)
    VideoRecordingHandler.stop()
