import cv2
import numpy as np

from camera.cameramodel import CameraModel


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

    def _get_rotation_matrix_from(self, rotation_vector):
        rotation_matrix, jacobian = cv2.Rodrigues(rotation_vector)
        return rotation_matrix

    def _get_extrinsic_parameters(self, rotation_matrix, translation_vector):
        return np.concatenate((rotation_matrix, translation_vector), axis=1)

    def _compute_camera_matrix(self, intrinsic_parameters, extrinsic_parameters):
        return np.dot(intrinsic_parameters, extrinsic_parameters)
