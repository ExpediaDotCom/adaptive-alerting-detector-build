from adaptivealerting.detectors.base import BaseDetector


def test_create_detector_():
    def my_train_fn():
        pass

    MyDetector = BaseDetector(name="My First Detector", train=my_train_fn)
