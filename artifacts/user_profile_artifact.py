from artifacts.meta_data_helper import MetaDataHelper


class UserProfileArtifact:

    def __init__(self) -> None:
        self.ip_address = MetaDataHelper.get_ip_address()
        self.mac_address = MetaDataHelper.get_mac_address()
