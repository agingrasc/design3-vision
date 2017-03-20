from detector.worldelement.iworldelementdetector import IWorldElementDetector


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
            self._detectors.append(detector)
