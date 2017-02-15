import json

from api.restapi import FlaskRESTAPI

from camera.camera import Camera
from camera.camera import CameraModel

if __name__ == "__main__":
    with open('./config/camera_model.json') as file:
        camera_parameters = json.load(file)

    camera = Camera(
        CameraModel(None, None, camera_parameters['camera_matrix'], None, None, None, None)
    )

    api = FlaskRESTAPI(static_folder='../static', camera_service=camera)

    api.run()
