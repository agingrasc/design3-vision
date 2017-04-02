from mock import mock
from unittest import TestCase

from domain.detector.worldelement.iworldelementdetector import IWorldElementDetector
from domain.world.worldelement import WorldElement
from service.image.detectonceproxy import DetectOnceProxy


class DetectOnceProxyTest(TestCase):
    def setUp(self):
        self.mock_image = mock.Mock()
        self.mock_detector = mock.create_autospec(IWorldElementDetector)
        self.detect_once_proxy = DetectOnceProxy(self.mock_detector)

    def test_given_a_new_detect_once_proxy_it_has_not_detected_an_element(self):
        self.assertFalse(self.detect_once_proxy.has_detected())

    def test_given_a_new_detector_when_detecting_an_element_then_it_has_detected(self):
        self.detect_once_proxy.detect(self.mock_image)

        self.assertTrue(self.detect_once_proxy.has_detected())

    def test_given_a_detector_that_has_detected_an_element_when_detecting_again_return_the_same_detected_object(self):
        first_time_detected_object = mock.create_autospec(WorldElement)
        self.mock_detector.detect.return_value = first_time_detected_object
        self.detect_once_proxy.detect(self.mock_image)

        second_time_detected_object = self.detect_once_proxy.detect(self.mock_image)

        self.assertEquals(first_time_detected_object, second_time_detected_object)

    def test_given_a_detector_that_has_detected_when_resetting_the_detector_then_it_has_not_detected(self):
        self.detect_once_proxy.detect(self.mock_image)

        self.detect_once_proxy.reset_detection()

        self.assertFalse(self.detect_once_proxy.has_detected())
