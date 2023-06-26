#Imported Modules
from os import error
import time
import psutil
from artifacts.user_profile_artifact import UserProfileArtifact
from database import DatabaseService
import gridfs
from pymongo import MongoClient
from artifacts.meta_data_helper import MetaDataHelper
import subprocess

# MAY WANT TO CONSIDER PACKAGING TOGETHER EVERYTHING AT ONCE
class Processes:

    @staticmethod
    def start():
        commands = ["ps", "-aux"]
        practice = subprocess.Popen(commands, stdout=subprocess.PIPE)
        text = str(practice.stdout.read())
        text = text.split('\\n')
        i = 0
        processInfo = []
        while i < len(text):
            processInfo.append(text[i])
            i += 1
        
        processInfo.pop(0)
        fileLines = sum(1 for line in processInfo)   #length of list

        newList = []
        i = 1
        while i < fileLines:
            temp = []
            practice = processInfo[i].split(' ')
            i += 1
            j=0
            while j < len(practice):
                if practice[j] != '':
                    temp.append(practice[j])
                j += 1
            newList.append(temp)

        commands = ["ps", "-e"]
        pname= str(subprocess.Popen(commands, stdout=subprocess.PIPE).stdout.read())
        pname = pname.split('\\n')
        k = 1
        pnameArray = []
        while k < len(pname)-1:
            pname[k] = pname[k].split()
            pnameArray.append(pname[k][3])
            k += 1


        client = MongoClient(port = 27017)
        db = client.AVERT
        fs = gridfs.GridFS(db)
        database = DatabaseService(client, db, fs)
        finalList = []
        i = 0;
        while i < len(newList)-1:
            try:
                tempList = [None] * 14          #Set up temp array
                tempList[0] = newList[i][0]      #username used to run the process
                tempList[1] = pnameArray[i]      #Process Name
                tempList[2] = newList[i][1]      #PID
                #set up access to PPID 
                ppid= str(subprocess.Popen(["ps", "-o", "ppid=", "-p", str(newList[i][1])], stdout=subprocess.PIPE).stdout.read())
                ppid = ppid.split()
                ppid = ppid[1].split('\\n')
                tempList[3] = ppid[0]                #get PPID
                tempList[4] = newList[i][8]         #startime
                tempList[5] = newList[i][10]        #COMMAND - ERROR as the strSPLIT messed up some commands
                tempList[6] = newList[i][6]         #TERMINAL
                tempList[7] = newList[i][7]          #STATUS
                tempList[8] = newList[i][3]          # %MEM - asks for ratio
                tempList[9] = newList[i][2]         # CPU%
                tempList[10] = newList[i][0]         # P Privileges
                ppriority= str(subprocess.Popen(["ps", "-o", "pri", "-p", str(newList[i][1])], stdout=subprocess.PIPE).stdout.read())
                ppriority = ppriority.split()
                ppriority = ppriority[1].split('\\n')
                tempList[11] = [ppriority[0]]       # P Priority
                ptype = 'Background'
                if '+' in newList[i][7]:
                    ptype = 'Foreground'
                tempList[12] = [ptype]                   # P Type
                t = psutil.Process(int(newList[i][1])).num_threads()
                tempList[13] = [t]                   #No. of thread
                finalList.append(tempList)
                #THIS IS THE FINAL LIST AS ASKED FOR BY THE SRS - THREADS NOT ASKED FOR
                i += 1
            except IndexError as e:
                i +=1

        for l in finalList:
            database.process_db_write(l[0], l[1],l[2],l[3],l[4],l[5],l[6],l[7],l[8],l[13],l[9],l[10],l[11],l[12], MetaDataHelper.get_zulu_time(), UserProfileArtifact().__dict__, [], [] )

    # END ----------------------------------------------------------------
    #process not setting up atm
