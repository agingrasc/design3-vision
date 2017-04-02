from domain.detector.worldelement.iworldelementdetector import IWorldElementDetector


class DetectOnceProxy(IWorldElementDetector):
    def __init__(self, detector):
        self._detector = detector
        self._has_detected = False
        self._detected_element = None

    def detect(self, image):
        if self._has_detected:
            return self._detected_element
        else:
            self._detected_element = self._detector.detect(image)
            self._has_detected = True
            return self._detected_element

    def reset_detection(self):
        self._has_detected = False

    def has_detected(self):
        return self._has_detected
