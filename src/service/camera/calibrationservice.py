from camera.calibration import Calibration
from camera.calibration import CalibrationTargetNotFoundError
from camera.camerafactory import CameraFactory


class CalibrationService:
    def __init__(self, camera_factory):
        if isinstance(camera_factory, CameraFactory):
            self._camera_factory = camera_factory
        else:
            raise TypeError("instance is not of type {}".format(CameraFactory.__name__))

    def create_calibration(self, target_shape):
        calibration = Calibration(target_shape, self._camera_factory)
        return calibration

    def calibrate_from_images(self, target_shape, images):
        calibration = self.create_calibration(target_shape)

        for image in images:
            try:
                calibration.collect_target_image(image)
            except CalibrationTargetNotFoundError:
                print("Calibration target not found on image, skipping image")
                continue

        camera_model = calibration.do_calibration()
        return camera_model
