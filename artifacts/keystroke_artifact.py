from artifacts.artifact import Artifact


class KeystrokeArtifact(Artifact):

    def __init__(self, pressed_key) -> None:
        self.key_press = pressed_key
        self.type = "keystroke"
