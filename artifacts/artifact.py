from artifacts.user_profile_artifact import UserProfileArtifact
from artifacts.meta_data_helper import MetaDataHelper


class Artifact:

    def __init__(self) -> None:
        self.user_profile = UserProfileArtifact()
        self.time_stamp = MetaDataHelper.get_zulu_time()
        self.tags = ""
        self.annotations = ""
