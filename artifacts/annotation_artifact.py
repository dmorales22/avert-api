from artifacts.meta_data_helper import MetaDataHelper
from artifacts.user_profile_artifact import UserProfileArtifact


class AnnotationArticact:

    def __init__(self) -> None:
        self.timestamp = MetaDataHelper.get_zulu_time()
        self.description = ""
        self.user_profile = UserProfileArtifact().__dict__
