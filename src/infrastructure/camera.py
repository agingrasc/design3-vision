import json

from camera.camera import CameraModel


class JSONCameraModelRepository:
    def __init__(self, file):
        self._models = {}
        self._file = file

        self._load_models_from(self._file)

    def get_all_camera_model(self):
        return [camera_model for camera_model in self._models.items()]

    def get_camera_model_by_id(self, id):
        return self._models.get(id)

    def add_camera_model(self, camera_model):
        self._models[camera_model.get_id()] = camera_model

    def _load_models_from(self, file):
        with open(file, 'r') as data:
            camera_models_data = json.load(data)

        for camera_model_dto in camera_models_data:
            camera_model = CameraModel(
                camera_model_dto['id'],
                camera_model_dto['intrinsic_parameters'],
                camera_model_dto['extrinsic_parameters'],
                camera_model_dto['camera_matrix'],
                camera_model_dto['distortion_coefficients'],
                camera_model_dto['rotation_matrix'],
                camera_model_dto['translation_vector'],
                camera_model_dto['origin_image_coordinates']
            )
            self.add_camera_model(camera_model)
