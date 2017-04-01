import cv2

from unittest import TestCase

from camera.camerafactory import CameraFactory
from camera.calibration import Calibration, CalibrationTargetNotFoundError


class CalibrationTest(TestCase):
    def setUp(self):
        self._a_calibration = Calibration(self._calibration_target_shape, self._camera_factory)
        self._camera_factory = CameraFactory()
        self._calibration_target_shape = (9, 6)

    def test_given_an_image_with_a_valid_calibration_target_when_adding_the_image_it_registers_it(self):
        image_with_valid_calibration_target = cv2.imread(
            './test/acceptance/fixture/image_with_a_valid_calibration_target.jpg')

        self._a_calibration.collect_target_image(image_with_valid_calibration_target)

        self.assertFalse(self._a_calibration.is_empty())

    def test_given_an_image_with_a_non_valid_target_when_adding_the_image_it_throws_an_error(self):
        image_with_non_valid_target = cv2.imread(
            './test/acceptance/fixture/image_with_a_non_valid_calibration_target.jpg')

        self.assertRaises(CalibrationTargetNotFoundError,
                          self._a_calibration.collect_target_image,
                          image_with_non_valid_target)
