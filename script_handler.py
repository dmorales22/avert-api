# 1. Expose an HTTP method '/generate_script' that takes in a list of selected artifact ids
# 2. In the method fetch the artifacts, filter out the ones that are usable (clicks and keystrokes)
# 3. Sort the artifacts by time
# 4. Have a template string for the method needed to do a keystroke/mouse action
# 5. Add a time.sleep(something) between each execution
# 6. Return the script and save it as a .py in the browser

from os import wait
from typing import List
import gridfs

from pymongo import MongoClient
from bson import json_util
from database import DatabaseService
import json
import database
import pyautogui


class ScriptHandler:

    # As a static method, given a list of artifact ids, wait time, and a database service, generate a .py script with the keystrokes/mouse actions
    @staticmethod
    def generate_script(artifact_ids: List[str], wait_time: float, db_service: DatabaseService) -> str:
        """Given a list of artifact ids, wait time, and a database service, generate a .py script with the keystrokes/mouse actions

        Args:
            artifact_ids (List[str]): A list of artical ids
            wait_time (float): The time to wait between each artifact action
            db_service (DatabaseService): Service to access the database

        Returns:
            str: A string of the script

        Author:
            Timothy P. McCrary

        Pre-conditions:
            @requires artifact_ids, wait_time, and db_service are not None or empty

        Post-conditions:
            @ensures \\result is a string of formatted python code 

        """
        client = MongoClient(port=27017)
        db = client.AVERT
        fs = gridfs.GridFS(db)
        db_service = database.DatabaseService(client, db, fs)

        # Go through each artifact id and get the artifact from the database and put it in a list of artifacts
        artifacts: List = ScriptHandler.__get_artifacts(
            artifact_ids, db_service)

        # Filter out the artifacts that are not usable (clicks and keystrokes)
        usable_artifacts = ScriptHandler.__filter_artifacts(artifacts)

        # Sort the artifacts by time
        sorted_artifacts = ScriptHandler.__sort_artifacts(usable_artifacts)

        # Generate the script
        script = ScriptHandler.__generate_script_string(
            sorted_artifacts, wait_time)

        return script

    # Static function, given a list of artifacts, returns the articafts whose type is either 'mouse_action' or 'keystroke'

    @staticmethod
    def __filter_artifacts(artifacts: List) -> List[dict]:
        """Given a list of artifacts, returns the articafts whose type is either 'mouse_action' or 'keystroke'

        Args:
            artifacts (List): A list of artifacts

        Returns:
            List[dict]: A list of artifacts whose type is either 'mouse_action' or 'keystroke'

        Author:
            Timothy P. McCrary
        Pre-conditions:
            @requires artifacts is not None or empty

        Post-conditions:
            @ensures \\result is a list of artifacts whose type is either 'mouse_action' or 'keystroke'
        """

        filtered_artifacts = []
        for artifact in artifacts:
            if artifact["type"] == 'mouse_action' or artifact["type"] == 'keystroke':
                filtered_artifacts.append(artifact)
        return filtered_artifacts

    # Static function, given a list of artifacts, returns the artifacts sorted by artifact.timestamp

    @staticmethod
    def __sort_artifacts(artifacts: List) -> List[dict]:
        """Given a list of artifacts, returns the artifacts sorted by artifact.timestamp

        Args:
            artifacts (List): A list of artifacts

        Returns:
            List[dict]: A list of artifacts sorted by artifact.timestamp

        Author:
            Timothy P. McCrary

        Pre-conditions:
            @requires artifacts is not None or empty

        Post-conditions:
            @ensures \\result is a list of artifacts sorted by artifact.timestamp

        """
        sorted_artifacts = sorted(
            artifacts, key=lambda artifact: artifact["artifact"]["timestamp"])
        return sorted_artifacts

    # Static function, given a list of artifacts and a wait time, returns a string of python code that can be executed to perform the actions

    @staticmethod
    def __generate_script_string(artifacts: List, wait_time: float) -> str:
        """Given a list of artifacts and a wait time, returns a string of python code that can be executed to perform the actions

        Args:
            artifacts (List): A list of artifacts
            wait_time (float): The time to wait between each artifact action

        Returns:
            str: A string of python code that can be executed to perform the actions

        Author:
            Timothy P. McCrary

        Pre-conditions:
            @requires artifacts and wait_time are not None or empty

        Post-conditions:
            @ensures \\result is a string of python code that can be executed to perform the actions

        """

        # Go through each artifact, get the current and next artifact, and generate the script string
        script_string = f'import pyautogui\n'

        for i in range(len(artifacts)):
            current_artifact = artifacts[i]
            next_artifact = artifacts[i+1] if i+1 < len(artifacts) else None
            # If the current artifact is a mouse action, generate the mouse action script string
            if current_artifact["type"] == 'mouse_action':
                script_string += ScriptHandler.__generate_mouse_action_string(
                    current_artifact, next_artifact, wait_time)
            elif current_artifact["type"] == 'keystroke':
                script_string += ScriptHandler.__generate_keystroke_string(
                    current_artifact, wait_time)

        return script_string

    # Private static function, given an mouse action artifact and wait time, returns a string of formated python code that can be executed to perform the action
    @staticmethod
    def __generate_mouse_action_string(current_artifact: dict, next_artifact: dict, wait_time: float) -> str:
        """Given an mouse action artifact and wait time, returns a string of formated python code that can be executed to perform that mouse action

        Args:
            current_artifact (dict): The current artifact
            next_artifact (dict): The next articfract
            wait_time (float): The time to wait between each artifact action

        Returns:
            str: A string of python code that can be executed to perform the action

        Author:
            Timothy P. McCrary

        Pre-conditions:
            @requires current_artifact, next_artifact, and wait_time are not None or empty

        Post-conditions:
            @ensures \\result is a string of python code that can be executed to perform a mouse action
        """

        if current_artifact["mouse_action"] != "down":
            return ""

        pause_string: str = ""
        # If the current artifact and the next artifact are both mouse actions, enter
        if next_artifact is not None and next_artifact["type"] == 'mouse_action':
            # # If teh current artifact position is not the same as the next artifact position, then add pause
            # if current_artifact["mouse_action_value"] != next_artifact["mouse_action_value"]:
            #     pause_string = f'pyautogui.PAUSE = {wait_time}\n'
            # If the current artifact position is not the same as the next artifact position within a certain threshold, then add pause
            if abs(current_artifact["mouse_action_value"][0] - next_artifact["mouse_action_value"][0]) > 2 and abs(current_artifact["mouse_action_value"][1] - next_artifact["mouse_action_value"][1]) > 2:
                pause_string = f'pyautogui.PAUSE = {wait_time}\n'

        # If the artifact button is 'left' or 'right', use the pyautogui.click or pyautogui.rightClick method
        click_string: str = ''
        if current_artifact["button"] == 'left':
            click_string = f'pyautogui.click()'
        elif current_artifact["button"] == 'right':
            click_string = f'pyautogui.rightClick()'

        return f'pyautogui.moveTo({current_artifact["mouse_action_value"][0]}, {current_artifact["mouse_action_value"][1]})\n{click_string}\n{pause_string}'

    # Private static function, given an keystroke artifact and wait time, returns a string of formated python code that can be executed to perform the action

    @staticmethod
    def __generate_keystroke_string(artifact: dict, wait_time: float) -> str:
        """ Given an keystroke artifact and wait time, returns a string of formated python code that can be executed to perform a keystroke action

        Args:
            artifact (dict): The artifact
            wait_time (float): The time to wait between each artifact action

        Returns:
            str: A string of python code that can be executed to perform the action

        Author:
            Timothy P. McCrary

        Pre-conditions:
            @requires artifact and wait_time are not None or empty

        Post-conditions:
            @ensures \\result is a string of python code that can be executed to perform a keystroke action
        """
        # if the artifact key_press is "^M", then use pyautogui.press("enter")
        if artifact["key_press"] == "\r":
            return f'pyautogui.press("enter")\npyautogui.PAUSE = {wait_time}\n'
        return f'pyautogui.typewrite("{artifact["key_press"]}")\npyautogui.PAUSE = {wait_time}\n'

    # Private static function, given a string, create a python file with the string and save it to the filesystem

    @staticmethod
    def save_script_to_file(script: str, file_name: str) -> None:
        """Given a string, create a python file with the string and save it to the filesystem

        Args:
            script (str): The string of python code
            file_name (str): The name of the file to save the script to

        Returns:
            None

        Author:
            Timothy P. McCrary

        Pre-conditions:
            @requires script and file_name are not None or empty

        Post-conditions:
            @ensures \\result is None
        """
        with open(file_name, 'w') as f:
            f.write(script)

    # Private static function, given a list of artifacts, print them out

    @staticmethod
    def __print_artifacts(artifacts: List) -> None:
        """ Given a list of artifacts, print them out

        Args:
            artifacts (List): The list of artifacts

        Returns:
            None

        Author:
            Timothy P. McCrary

        Pre-conditions:
            @requires artifacts is not None or empty

        Post-conditions:
            @ensures \\result is None
        """
        for artifact in artifacts:
            print(json.dumps(json.loads(json_util.dumps(
                artifact)), sort_keys=False, indent=4))

    # Private static function, given a list of artifact ids, get the artifacts from the database and return them without none types

    @staticmethod
    def __get_artifacts(artifact_ids: List[str], db_service: DatabaseService) -> List[dict]:
        """ Given a list of artifact ids, get the artifacts from the database and return them without none types

        Args:
            artifact_ids (List[str]): The list of artifact ids
            db_service (DatabaseService): The database service

        Author:
            Timothy P. McCrary

        Returns:
            List[dict]: The list of artifacts without none types

        Pre-conditions:
            @requires artifact_ids and db_service are not None or empty

        Post-conditions:
            @ensures \\result is a list of artifacts without none types
        """
        artifacts = []
        for artifact_id in artifact_ids:
            artifact = db_service.database_query_id(artifact_id)
            if artifact is not None:
                artifacts.append(artifact)
        return artifacts


if __name__ == '__main__':
    pyautogui.typewrite("^M")
    pyautogui.typewrite("^M")

    pyautogui.press('enter')
    pyautogui.typewrite("^M")

    pyautogui.press('^M')
    pyautogui.typewrite("^M")

    # pyautogui.typewrite("return")
    exit()
    client = MongoClient(port=27017)
    db = client.AVERT
    fs = gridfs.GridFS(db)
    dbs = DatabaseService(client, db, fs)
    artifact_ids: List = ["6181d29d63987ebc9fd1c8b0",
                          "6181d29d63987ebc9fd1c8b2",
                          "6181d29e63987ebc9fd1c8b4",
                          "6181d29e63987ebc9fd1c8b6",
                          "6181d29f63987ebc9fd1c8b8",
                          "6181d2a063987ebc9fd1c8ba",
                          "6181d2a063987ebc9fd1c8bc",
                          "6181d2a063987ebc9fd1c8be",
                          "6181d2a063987ebc9fd1c8c0",
                          "6181d2a063987ebc9fd1c8c2",
                          "6181d2a163987ebc9fd1c8c4",
                          "6181d2a163987ebc9fd1c8c6",
                          "6181d2a563987ebc9fd1c8c8",
                          "6181d2a563987ebc9fd1c8ca",
                          "6181d2a963987ebc9fd1c8cc",
                          "6181d2a963987ebc9fd1c8ce",
                          "6181d2a963987ebc9fd1c8d0",
                          "6181d2a963987ebc9fd1c8d2",
                          "6181d2a3fc63a8b6dad1c97d",
                          "6181d2a3fc63a8b6dad1c97f",
                          "6181d2a3fc63a8b6dad1c981",
                          "6181d2a3fc63a8b6dad1c983",
                          "6181d2aafc63a8b6dad1c985",
                          "6181d2aafc63a8b6dad1c987"]
    script: str = ScriptHandler.generate_script(artifact_ids, 0.18, dbs)
    print(script)
    ScriptHandler.save_script_to_file(script, 'generated_script_test.py')
