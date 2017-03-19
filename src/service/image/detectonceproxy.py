from detector.worldelement.iworldelementdetector import IWorldElementDetector


class DetectOnceProxy(IWorldElementDetector):
    def __init__(self, detector):
        self._detector = detector
        self._is_detected = False
        self._detected_element = None

    def detect(self, image):
        if self._is_detected:
            return self._detected_element
        else:
            self._detected_element = self._detector.detect(image)
            self._is_detected = True
            return self._detected_element
