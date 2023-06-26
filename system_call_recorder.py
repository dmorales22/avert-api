
# from ptrace.syscall import ptrace_syscall
# import ptrace
import gridfs
from ptrace import syscall, debugger, logging_tools
import os
from typing import Dict, List
import psutil
import subprocess

from pymongo.mongo_client import MongoClient

from database import DatabaseService
from system_call_parser import SystemCallParser
from artifacts.meta_data_helper import MetaDataHelper
from artifacts.user_profile_artifact import UserProfileArtifact
import pymp
from threading import Thread


class SystemCallRecorder:

    # def __init__(self) -> None:
    #     pass

    @staticmethod
    def start(database_service: DatabaseService) -> None:
        """ Starts the system call recorder.

        Args:
            database_service (DatabaseService): The database service.
        
        Author:
            Timothy P. McCrary

        Pre-condition:
            @requires database_service is not None or empty
        
        Post-condition:
            @ensures \\result is None
        """

        # TODO: Use strace -o <./output.txt> -t ls
        # WRITING SYSTEM CALL
        # def systemcall_db_write(self, syscall_name, syscall_arg, syscall_return_value, syscall_type, timestamp, user_profile, tags, annotation):
        # artifact = {
        #     ser_profile": user_profile,
        #     "timestamp": timestamp,
        #     "tags": tags,
        #     "annotations": annotation
        # }
        # system_call = {
        #     "artifact": artifact,
        #     "systemcall_name": syscall_name,
        #     "systemcall_args": syscall_arg,
        #     "systemcall_return_value": syscall_return_value,
        #     "systemcall_type": syscall_type,
        #     "type": "system_call"
        # }

        # result = self.db.SystemCall.insert_one(system_call)
        # print(result)

        SystemCallRecorder.trace_system_calls(database_service)

        pass
    
    @staticmethod
    def trace_system_calls(database_service: DatabaseService) -> None:
        """ Gets a list of process and starts tracing them.

        Args:
            database_service (DatabaseService): The database service.

        Author:
            Timothy P. McCrary

        Pre-condition:
            @requires database_service is not None or empty
        
        Post-condition:
            @ensures \\result is None
        """

        pids: List[int] = psutil.pids()

        api_pid: int = os.getpid()

        # for pid in pids:
        #     thread = Thread(target=SystemCallRecorder.trace_pid, args=(pid, api_pid))
        #     thread.start()
        with pymp.Parallel() as parallel:
            for pid in parallel.iterate(pids):
                SystemCallRecorder.trace_pid(pid, api_pid)
        
          
    filtered_commands = ["strace", "mongo", "mongod", "avert", "electron", "/init", "vscode"]

    @staticmethod
    def trace_pid(pid: int, api_pid: int) -> None:
        """ Given a process id, starts tracing its system calls.

        Args:
            pid (int): The process id.
            api_pid (int): The api process id.

        Author:
            Timothy P. McCrary

        Pre-condition:
            @requires pid and api_pid is not None or empty.

        Post-condition:
            @ensures \\result is None
        """
        # Skip the AVERT API pid.   
        some_process = psutil.Process(pid)
        process_cmd:str = some_process.cmdline()
        if (pid == api_pid or some_process.ppid() == api_pid or process_cmd.__contains__("strace") or process_cmd.__contains__("mongo") or process_cmd.__contains__("mongod") or process_cmd.__contains__("avert") or process_cmd.__contains__("electron")):
            # print(f"PROCESS NOT TRACED {pid}")
            return

        for filter_command in SystemCallRecorder.filtered_commands:
            for cmd in process_cmd:
                if (filter_command in cmd):
                    # print(f"PROCESS NOT TRACED {pid}")
                    return

        # print(f"TRACING {pid}")


        strace_process: subprocess.Popen = subprocess.Popen(["strace", "-p", f"{pid}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output: str = strace_process.stderr.readline().decode("utf-8")

        # For debugging
        # file = open(f"log_{pid}", "a")
        count = 0
        while strace_process.poll() is None:
            if (output != strace_process.stderr.readline().decode("utf-8")):
                output = strace_process.stderr.readline().decode("utf-8")
                # For debugging
                # file.write(output)
                parced_call: Dict = SystemCallParser.parse_system_call(output)
                # file.write(str(parced_call))

                if (parced_call != None):
                    client = MongoClient(port=27017)
                    db = client.AVERT
                    fs = gridfs.GridFS(db)
                    database_service = DatabaseService(client, db, fs)
                    
                    database_service.systemcall_db_write(parced_call["name"], parced_call["args"], parced_call["return"], parced_call["type"], MetaDataHelper.get_zulu_time(), UserProfileArtifact().__dict__, [], [])

            count += 1
            if count > 10:
                return
        # For debugging
        # file.close()

                


if __name__ == '__main__':
    SystemCallRecorder.start(None)
