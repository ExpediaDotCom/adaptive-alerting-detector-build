

class base_detector:
    """Base class for detectors."""

    def __init__(self, **kwargs):
        pass

    def train(self):
        raise NotImplementedError

    def save(self):
        pass

    def update(self):
        pass