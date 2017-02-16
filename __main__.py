import json
import os

from api.restapi import FlaskRESTAPI

from camera.camera import CameraModel


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
    camera_model = load_camera_model_from('./config/camera_model.json')

    api = FlaskRESTAPI(
        static_folder=os.path.abspath('./static'),
        camera_service=camera_model
    )

    api.run()
