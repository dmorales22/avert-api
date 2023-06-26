from pymongo import MongoClient
import os
from bson import ObjectId
import base64


def add_path(filename):
    """
        purpose: Annotates filename with ".pcap"extenstion

        @requires filename to not be null or empty
        
        @ensures /result returns created path for filename that was given 
    """
    return "./pcap/" + filename


def add_absolute_path(filename):
    """
        purpose: returns the filename with path

        @requires filename to not be null or empty

        @ensures /result returns absolute path if file name is valid
    """
    filename_with_path = add_path(filename)
    return os.path.abspath(filename_with_path)


def get_pcap(pcap_id):
    """
        Purpose: gets pcap file from database with specific pcap ID

        @requires pcap_id to not be null or empty

        @ensures /result returns decoded pcap file contents and filename 
    """
    print(pcap_id)

    client = MongoClient(port=27017)
    db = client.AVERT

    result = db.NetworkActivity.find_one({'_id': ObjectId(pcap_id)})
    filename = add_absolute_path(result['PCAPFile'])
    f = open(filename, 'rb')
    r = f.read()

    content = base64.b64encode(r).decode()

    # return {"content": content, "filename": "2138631287.pcap"}
    return {"content": content}


def main():
    """
        purpose: Established database connection and filename

        @requires AVERT must be connected to database

        @ensure /result successful pcap file given
    """
    pcap_id = '61817d5c244331daf5c46d9d'
    client = MongoClient(port=27017)
    db = client.AVERT

    result = db.NetworkActivity.find_one({'_id': ObjectId(pcap_id)})
    filename = add_absolute_path(result['PCAPFile'])
    f = open(filename, 'rb')
    r = f.read()
    print(r)
    print(type(r))

    print(base64.b64encode(r).decode())
    print(type(base64.b64encode(r).decode()))
    print('End of transmission. Don\'t panic!')


if __name__ == '__main__':
    main()
