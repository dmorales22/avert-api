from artifacts.user_profile_artifact import UserProfileArtifact
from database import DatabaseService
import gridfs
from pymongo import MongoClient
from artifacts.meta_data_helper import MetaDataHelper
import subprocess
import time
from datetime import datetime, timezone
import os 

class CommandHistory:
    @staticmethod
    def start():
        """
            purpose: Initiates the command name history

            @requires: avert to be running

            @ensures /result a thread is spawned that writes a new hsitory instance every time a command is entered
        """
        CommandHistory.log_command_history()

    @staticmethod
    def add_commands(command_list, database):
        """
            purpose: adds command to the command list

            @requires command_list and database to not be null or empty

            @ensures /result dictionary with command name, arguments, and type
        """
        for i in range(len(command_list)): # Runs a loop through added command list
            command_args_list = command_list[i].split() # Splits elements
            command_name = command_args_list[1] # Gets command name 
            command_args = command_args_list[2:] # Gets commands arguments
            database.systemcall_db_write(command_name, command_args, MetaDataHelper.get_zulu_time(), UserProfileArtifact().__dict__, [], []) 

    @staticmethod
    def log_command_history():
        """
            purpose: logging all commands entered as input as long as they are not duplicates

            @requires AVERT to be running
            @requires AVERT to be connected to database

            @ensures /result written command to database
        """
        previous_list = []
        client = MongoClient(port=27017)
        db = client.AVERT
        fs = gridfs.GridFS(db)
        database = DatabaseService(client, db, fs)
        username = os.getlogin()  # Gets username of current session

        config_path = "/home/" + username + "/.bashrc" # Creates absolute path of bash config 
        rewrite_config_command = "cp .bashrc " + config_path
        subprocess.Popen(rewrite_config_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        subprocess.Popen("sudo chsh -s /bin/bash", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        with open(config_path, 'a+') as bash_config: # Reads through the bash config
            bash_config.seek(0) # Points at beginning of file
            if 'shopt -s histappend' not in bash_config.read(): # Checks if this config line is in file
                bash_config.write('shopt -s histappend\n') # Appends at end of file if it doesn't exist.
            bash_config.seek(0)
            if 'PROMPT_COMMAND="history -a;$PROMPT_COMMAND"' not in bash_config.read():
                bash_config.write('PROMPT_COMMAND="history -a;$PROMPT_COMMAND"\n')

        subprocess.Popen("sudo chsh -s /bin/bash", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ran_once = False 
        while True: #Runs loop until exited
            bash_command = "cat -n /home/" + username + "/.bash_history | tail -n 3"
            commands = subprocess.Popen(bash_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            command_list = commands.communicate()[0].decode("utf-8").split('\n') #Splits the output into a list 

            added_commands = list(set(command_list) - set(previous_list)) #Checks added commands using a set
            #print("Added:", added_commands)

            if ran_once: # Skips over first iteration since it pulls previous commands
                if not added_commands: # Continues loop if no command is ran in terminal
                    time.sleep(1.0) # Runs every second 
                    continue

                CommandHistory.add_commands(added_commands, database) # Writes to database when new commands are detected 

            previous_list = command_list 
            ran_once = True 
            time.sleep(1.0) # Runs every second 
            
#CommandHistory.start()
