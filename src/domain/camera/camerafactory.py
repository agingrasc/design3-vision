import cv2
import numpy as np

from domain.camera.cameramodel import CameraModel


class CameraFactory:
    def create_camera_model(self, intrinsic_parameters, translation_vector, rotation_vector,
                            distortion_coefficients, origin):
        rotation_matrix = self._get_rotation_matrix_from(rotation_vector)
        extrinsic_parameters = self._get_extrinsic_parameters(rotation_matrix, translation_vector)
        camera_matrix = self._compute_camera_matrix(intrinsic_parameters, extrinsic_parameters)

        return CameraModel(
            1,
            intrinsic_parameters,
            extrinsic_parameters,
            camera_matrix,
            distortion_coefficients,
            rotation_matrix,
            translation_vector,
            origin)

    def create_camera_model_dto(self, camera_model):
        return {
            "id": camera_model._id,
            "intrinsic_parameters": camera_model._intrinsic_parameters.tolist(),
            "extrinsic_parameters": camera_model._extrinsic_parameters.tolist(),
            "camera_matrix": camera_model._camera_matrix.tolist(),
            "rotation_matrix": camera_model._rotation_matrix.tolist(),
            "translation_vector": camera_model._translation_vector.tolist(),
            "distortion_coefficients": camera_model._distortion_coefficients.tolist(),
            "origin_image_coordinates": camera_model._target_origin.tolist()
        }

    def create_camera_model_from_dto(self, camera_model_dto):
        return CameraModel(
            camera_model_dto['id'],
            camera_model_dto['intrinsic_parameters'],
            camera_model_dto['extrinsic_parameters'],
            camera_model_dto['camera_matrix'],
            camera_model_dto['distortion_coefficients'],
            camera_model_dto['rotation_matrix'],
            camera_model_dto['translation_vector'],
            camera_model_dto['origin_image_coordinates']
        )

    def _get_rotation_matrix_from(self, rotation_vector):
        rotation_matrix, jacobian = cv2.Rodrigues(rotation_vector)
        return rotation_matrix

    def _get_extrinsic_parameters(self, rotation_matrix, translation_vector):
        return np.concatenate((rotation_matrix, translation_vector), axis=1)

    def _compute_camera_matrix(self, intrinsic_parameters, extrinsic_parameters):
        return np.dot(intrinsic_parameters, extrinsic_parameters)
