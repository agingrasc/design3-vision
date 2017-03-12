import os

from api.restapi import FlaskRESTAPI
from camera.camera import CameraFactory
from infrastructure.camera import JSONCameraModelRepository
from infrastructure.imagerepository import ImageRepository
from service.camera.calibrationservice import CalibrationService

if __name__ == "__main__":
    camera_model_repository = JSONCameraModelRepository('../data/camera_models/camera_models.json')
    camera_model = camera_model_repository.get_camera_model_by_id(0)

    camera_factory = CameraFactory()
    calibration_service = CalibrationService(camera_factory)
    image_repository = ImageRepository()

    api = FlaskRESTAPI(
        static_folder=os.path.abspath('../static'),
        camera_service=camera_model,
        calibration_service=calibration_service,
        image_repository=image_repository,
        camera_model_repository=camera_model_repository
    )

    api.run()
