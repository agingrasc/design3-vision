import mock

from unittest import TestCase

from domain.detector.worldelement.iworldelementdetector import IWorldElementDetector
from domain.world.worldelement import WorldElement
from service.image.detectonceproxy import DetectOnceProxy
from service.image.imagedetectionservice import ImageDetectionService


class ImageDetectionServiceTest(TestCase):
    def setUp(self):
        self.mock_detector = mock.create_autospec(IWorldElementDetector)
        self.an_image_detection_service = ImageDetectionService()

    def test_given_a_new_image_detection_service_when_registering_a_valid_detector_then_it_is_added(self):
        self.an_image_detection_service.register_detector(self.mock_detector)

        self.assertTrue(self.an_image_detection_service.detector_is_registered(self.mock_detector))

    def test_given_a_new_image_detection_service_when_registering_a_non_valid_detector_will_raise_type_error(self):
        self.assertRaises(TypeError, self.an_image_detection_service.register_detector, object())

    def test_given_an_image_detection_service_when_trying_to_register_twice_the_same_detector_throws_an_error(self):
        self.an_image_detection_service.register_detector(self.mock_detector)

        self.assertRaises(ValueError, self.an_image_detection_service.register_detector, self.mock_detector)

    def test_given_an_image_detection_service_with_detect_once_proxy_when_resetting_detectors_all_detectors_are_reset(
            self):
        detect_once_proxy_detector = mock.create_autospec(DetectOnceProxy)
        self.an_image_detection_service.register_detector(detect_once_proxy_detector)

        self.an_image_detection_service.reset_detection()

        detect_once_proxy_detector.reset_detection.assert_called_once()

    def test_given_an_image_detection_service_when_detecing_from_image_then_world_element_collection_is_returned(self):
        mock_image = mock.Mock()
        mock_world_element = mock.create_autospec(WorldElement)
        self.mock_detector.detect.return_value = mock_world_element
        self.an_image_detection_service.register_detector(self.mock_detector)

        world_elements = self.an_image_detection_service.detect_all_world_elements(mock_image)

        self.assertEquals(len(world_elements), 1)
        self.mock_detector.detect.assert_called_once()
        for element in world_elements:
            self.assertIsInstance(element, WorldElement)
