import math
import cv2
import numpy as np


class CameraModel:
    def __init__(self, id, intrinsic_parameters, extrinsic_parameters, camera_matrix,
                 distortion_coefficients, rotation_matrix, translation_vector, origin):
        self._id = id
        self._intrinsic_parameters = np.array(intrinsic_parameters)
        self._extrinsic_parameters = np.array(extrinsic_parameters)
        self._camera_matrix = np.array(camera_matrix)
        self._distortion_coefficients = np.array(distortion_coefficients)
        self._rotation_matrix = np.array(rotation_matrix)
        self._translation_vector = np.array(translation_vector)
        self._origin = np.array(origin)

    def get_id(self):
        return self._id

    def get_origin(self):
        return np.round(self._origin)[0].astype('int').tolist()

    def get_origin_orthogonal(self):
        x_axis = self.compute_world_to_image_coordinates(5, 0, 0)
        y_axis = self.compute_world_to_image_coordinates(0, 5, 0)

        return [
            tuple(x_axis),
            tuple(self.get_origin()),
            tuple(y_axis)
        ]

    def compute_world_to_image_coordinates(self, u, v, d):
        homogeneous_coordinates = np.dot(self._camera_matrix, np.array([u, v, d, 1]))
        return np.array([
            homogeneous_coordinates[0] / homogeneous_coordinates[2],
            homogeneous_coordinates[1] / homogeneous_coordinates[2]
        ]).astype('int').tolist()

    def compute_image_to_world_coordinates(self, u, v, d):
        m = self._camera_matrix
        A = np.array(m[0] - (u * m[2]))
        B = np.array(m[1] - (v * m[2]))

        u1 = A[:3]
        d1 = A[3]
        u2 = B[:3]
        d2 = B[3]
        u3 = np.array([0, 0, 1])
        d3 = d

        P = ((-d1 * np.cross(u2, u3)) + (-d2 * np.cross(u3, u1)) + (-d3 * np.cross(u1, u2))) / np.dot(u1.T,
                                                                                                      np.cross(u2, u3))

        return np.array(P, dtype=float).tolist()

    def transform_coordinates(self, transform_matrix, coordinate):
        homogeneous_coordinate = np.array([
            coordinate[0],
            coordinate[1],
            1
        ])
        return self._homogeneous_to_cart(np.dot(transform_matrix, homogeneous_coordinate))

    def _homogeneous_to_cart(self, coordinate):
        return [
            coordinate[0] / coordinate[2],
            coordinate[1] / coordinate[2]
        ]

    def compute_transform_matrix(self, angle, position):
        rad = np.deg2rad(angle)

        transform = np.array([
            [math.cos(rad), - math.sin(rad), position[0]],
            [math.sin(rad), math.cos(rad), position[1]],
            [0, 0, 1]
        ])

        return np.linalg.inv(transform)

    def undistort_image(self, image):
        return cv2.undistort(image, self._intrinsic_parameters, self._distortion_coefficients, None, None)

    def to_dto(self):
        return {
            "id": self._id,
            "intrinsic_parameters": self._intrinsic_parameters.tolist(),
            "extrinsic_parameters": self._extrinsic_parameters.tolist(),
            "camera_matrix": self._camera_matrix.tolist(),
            "rotation_matrix": self._rotation_matrix.tolist(),
            "translation_vector": self._translation_vector.tolist(),
            "distortion_coefficients": self._distortion_coefficients.tolist(),
            "origin_image_coordinates": self._origin.tolist()
        }
