from unittest import TestCase

from mock import mock

from domain.camera.calibration import Calibration
from domain.camera.camerafactory import CameraFactory
from service.camera.calibrationservice import CalibrationService


class CalibrationServiceTest(TestCase):
    def test_given_a_new_calibration_service_when_creating_a_calibration_then_returns_an_instance_of_a_calibration(
            self):
        camera_factory_mock = mock.create_autospec(CameraFactory)
        a_calibration_service = CalibrationService(camera_factory_mock)

        calibration = a_calibration_service.create_calibration((9, 6))

        self.assertIsInstance(calibration, Calibration)

    def test_when_trying_to_create_a_calibration_service_with_a_non_valid_camera_factory_object_then_throws_an_error(
            self):
        nonvalid_camera_factory = object()

        self.assertRaises(TypeError, CalibrationService, nonvalid_camera_factory)
