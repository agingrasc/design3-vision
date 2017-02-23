import json
import os

from api.restapi import FlaskRESTAPI
from camera.camera import CameraModel
from camera.camera import CameraFactory
from service.calibrationservice import CalibrationService
from infrastructure.imagerepository import ImageRepository


def load_camera_model_from(filepath):
    with open(filepath) as file:
        camera_parameters = json.load(file)

    return CameraModel(
        camera_parameters['intrinsic_parameters'],
        camera_parameters['extrinsic_parameters'],
        camera_parameters['camera_matrix'],
        None,
        camera_parameters['rotation_matrix'],
        camera_parameters['translation_vector'],
        camera_parameters['origin_image_coordinates']
    )


if __name__ == "__main__":
    camera_model = load_camera_model_from('../config/camera_model.json')

    camera_factory = CameraFactory()
    calibration_service = CalibrationService(camera_factory)
    image_repository = ImageRepository()

    api = FlaskRESTAPI(
        static_folder=os.path.abspath('../static'),
        camera_service=camera_model,
        calibration_service=calibration_service,
        image_repository=image_repository
    )

    api.run()
