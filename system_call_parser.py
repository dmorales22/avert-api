from re import split
import sys
from typing import Dict, List


class SystemCallParser:


    @staticmethod
    def parse_system_call(system_call: str) -> Dict or None:
        """ Given a system_call as a string, return a dictionary with the system call's name, arguments, return and type.

        Args:
            system_call (str): A system call as a string.

        Returns:
            Dict or None: A dictionary with the system call's name, arguments, return and type, or none if the system call is invalid.
        
        Author:
            Timothy P. McCrary

        Pre-condition:
            @requires system_call is not None or empty.

        Post-condition:
            @ensures \\result is a dictionary with the system call's name, arguments, return and type, or none if the system call is invalid.

        """

        if ('(' not in system_call or ')' not in system_call or '=' not in system_call):
            return None


        # if (system_call.count('(') > 1):

        equal_split: List[str] = system_call.rsplit('=', 1)
        call_split: List[str] = equal_split[0].split('(', 1)
        call_name: str = call_split[0].strip()
        call_split = call_split[1].rsplit(')', 1)
        call_args: str = call_split[0].strip()
        # call_split = call_split[1].split('=')
        call_return: str = equal_split[1].strip()


        # print(call_name)
        # print(call_args)
        # print(call_return)
        
        call_details: Dict = {}
        call_details["name"] = call_name
        call_details["args"] = call_args
        call_details["return"] = call_return
        call_details["type"] = SystemCallParser.get_sytem_call_type(call_name)

        return call_details
             

    @staticmethod
    def get_sytem_call_type(call_name: str) -> str:
        """ Given a system call's name, return its type.

        Args:
            call_name (str): A system call's name.

        Returns:
            str: The system call's type.

        Author:
            Timothy P. McCrary

        Pre-condition:
            @requires call_name is not None or empty.

        Post-condition:
            @ensures \\result is the system call's type.
        """

        process_control: List[str] = ["fork", "exit", "close"]
        file_management: List[str] = ["open", "read", "write", "close"]
        device_management: List[str] = ["ioctl", "read", "write"]
        info_maintenance: List[str] = ["getpid", "alarm", "sleep"]
        communication: List[str] = ["pipe", "shmget", "mmap"]

        if (call_name in process_control):
            return "Process Control"
        elif (call_name in file_management):
            return "File Management"
        elif (call_name in device_management):
            return "Device Management"
        elif (call_name in info_maintenance):
            return "Information Maintenance"
        elif (call_name in communication):
            return "Communication"
        else:
            return "Other"

if __name__ == '__main__':
    print("Testing SytemCallParser with hardcoded calls:")
    SystemCallParser.parse_system_call("mprotect(0x28c1c1340000, 262144, PROT_READ|PROT_WRITE) = 0")
    SystemCallParser.parse_system_call("read(17, \"\1\0\0\0\0\0\0\0\", 1024)      = 8")
    SystemCallParser.parse_system_call("strace: attach: ptrace(PTRACE_SEIZE, 14): Operation not permitted")
    SystemCallParser.parse_system_call("wait4(-1, 0x7ffe6afb5d9c, 0, NULL)      = ? ERESTARTSYS (To be restarted if SA_RESTART is set)")
    SystemCallParser.parse_system_call("mprotect(0x28c1c1340000, 262144, PROT_READ|PROT_WRITE) = 0")


