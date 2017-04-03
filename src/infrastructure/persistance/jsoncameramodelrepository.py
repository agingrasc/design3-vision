import json

from domain.camera.cameramodel import CameraModel


class JSONCameraModelRepository:
    def __init__(self, file, camera_factory):
        self._camera_factory = camera_factory
        self._camera_models = {}
        self._load_all_from(file)
        self._filename = file

    def find_all(self):
        return [camera_model for camera_model in self._camera_models.items()]

    def find_by_id(self, id):
        return self._camera_models.get(id)

    def add_camera_model(self, camera_model):
        if isinstance(camera_model, CameraModel):
            self._camera_models[camera_model.get_id()] = camera_model
        else:
            raise TypeError

    def persist(self):
        file = open(self._filename, 'w')
        json.dump([self._camera_factory.create_camera_model_dto(model) for model in self._camera_models.values()],
                  file, indent=4)
        file.close()

    def _load_all_from(self, file):
        with open(file, 'r') as data:
            camera_models_data = json.load(data)

        for camera_model_dto in camera_models_data:
            camera_model = self._camera_factory.create_camera_model_from_dto(camera_model_dto)
            self.add_camera_model(camera_model)
