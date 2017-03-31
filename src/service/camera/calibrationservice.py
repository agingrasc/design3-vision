from camera.calibration import Calibration
from camera.calibration import CalibrationTargetNotFoundError


class CalibrationService:
    def __init__(self, camera_factory):
        self._camera_factory = camera_factory

    def create_calibration(self, target_shape):
        calibration = Calibration(target_shape, self._camera_factory)
        return calibration

    def calibrate_from_images(self, images):
        calibration = self._camera_factory.create_calibration()

        for image in images:
            try:
                calibration.collect_target_image(image)
            except CalibrationTargetNotFoundError:
                print("Calibration target not found on image, skipping image")
                continue

        camera_model = calibration.do_calibration()
        return self._camera_factory.create_camera_model_dto(camera_model)
