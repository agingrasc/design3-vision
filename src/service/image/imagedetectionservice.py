from domain.detector.worldelement.iworldelementdetector import IWorldElementDetector
from domain.detector.worldelement.obstaclepositiondetector import ObstacleDetector
from service.image.detectonceproxy import DetectOnceProxy


class ImageDetectionService:
    def __init__(self):
        self._detectors = []

    def detect_all_world_elements(self, image):
        world_elements = []

        for detector in self._detectors:
            try:
                world_element = detector.detect(image)
                world_elements.append(world_element)
            except Exception as e:
                print("World initialisation failure: {}".format(type(e).__name__))

        return world_elements

    def register_detector(self, detector):
        if isinstance(detector, IWorldElementDetector):
            if not self.detector_is_registered(detector):
                self._detectors.append(detector)
            else:
                raise ValueError
        else:
            raise TypeError

    def reset_detection(self):
        for detector in self._detectors:
            if isinstance(detector, DetectOnceProxy):
                detector.reset_detection()

    def reset_obstacles(self):
        for detector in self._detectors:
            if isinstance(detector, DetectOnceProxy):
                if isinstance(detector._detector, ObstacleDetector):
                    detector.reset_detection()

    def detector_is_registered(self, detector):
        return detector in self._detectors
