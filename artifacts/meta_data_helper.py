import socket
from datetime import datetime, timezone
from uuid import getnode


class MetaDataHelper:

    @staticmethod
    def get_ip_address() -> str:
        """Gets IP address on local machine.

        Returns:
            str: Local IP address
        """
        s: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP: str = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    @staticmethod
    def get_mac_address() -> str:
        """Gets MAC address of local machine.

        Returns:
            str: Local MAC address
        """
        mac: int = getnode()

        return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

    @staticmethod
    def get_zulu_time() -> datetime:
        """ Gets current Zulu time.

        Returns:
            str: Current Zulu time
        """
        return datetime.now(timezone.utc)
        # date_str:str = str(datetime.now(timezone.utc).isoformat()[:-12]) + 'Z'
        # return date_str
        # return datetime.now(timezone.utc).isoformat()
