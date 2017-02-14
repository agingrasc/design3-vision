import cv2
import json
import numpy as np

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


class Camera:
    def __init__(self, camera_model=None):
        self.camera_model = camera_model

        self.target_points = []
        self.target_image_points = []
        self.target_object_points = []

        self.calibration_images = []
        self.reference_image_index = 0

    def image_to_world_coordinate(self, x, y, z):
        return self.camera_model.compute_image_to_world_coordinates(x, y, z)

    def add_image_for_calibration(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        has_corners, corners = cv2.findChessboardCorners(image, (9, 6), None)
        if has_corners:
            self.target_object_points.append(self.target_points)
            self.calibration_images.append(image)

            corners = cv2.cornerSubPix(image, corners, (5, 5), (-1, -1), criteria)
            self.target_image_points.append(corners)

    def add_target_points(self, target_points):
        self.target_points = target_points

    def calibrate(self):
        (
            ret,
            intrinsic_parameters,
            distortion_coefficients,
            rotation_vectors,
            translation_vectors
        ) = self.get_calibration_parameters(self.reference_image_index)

        translation_vector = translation_vectors[self.reference_image_index]
        rotation_matrix = self.get_rotation_matrix_from(rotation_vectors[self.reference_image_index])
        extrinsic_parameters = np.concatenate((
            rotation_matrix, translation_vectors[self.reference_image_index]), axis=1)
        camera_matrix = self.compute_camera_matrix(intrinsic_parameters, extrinsic_parameters)

        self.camera_model = CameraModel(
            intrinsic_parameters,
            extrinsic_parameters,
            camera_matrix,
            distortion_coefficients,
            rotation_matrix,
            translation_vector,
            self.target_image_points[0][0])

    def compute_camera_matrix(self, intrinsic_parameters, extrinsic_parameters):
        return np.dot(intrinsic_parameters, extrinsic_parameters)

    def get_rotation_matrix_from(self, rotation_vector):
        rotation_matrix, jacobian = cv2.Rodrigues(rotation_vector)
        return rotation_matrix

    def get_calibration_parameters(self, calibration_image_index):
        return cv2.calibrateCamera(
            self.target_object_points,
            self.target_image_points,
            self.calibration_images[calibration_image_index].shape[::-1],
            None, None
        )

    def undistort_image(self, image):
        return cv2.undistort(image,
                             self.camera_model.intrinsic_parameters,
                             self.camera_model.distortion_coefficients,
                             None, None)


class CameraModel:
    def __init__(self, intrinsic_parameters, extrinsic_parameters, camera_matrix,
                 distortion_coefficients, rotation_matrix, translation_vector, origin):
        self.intrinsic_parameters = intrinsic_parameters
        self.extrinsic_parameters = extrinsic_parameters
        self.camera_matrix = camera_matrix
        self.distortion_coefficients = distortion_coefficients
        self.rotation_matrix = rotation_matrix
        self.translation_vector = translation_vector
        self.origin = origin

    def compute_image_to_world_coordinates(self, u, v, z):
        m = self.camera_matrix

        object_x = ((-m[0][3] + u * m[2][3]) * (m[1][1] - v * m[2][1]) - (m[1][3] - v * m[2][3]) * (
            -m[0][1] + u * m[2][1])) / \
                   ((m[0][0] - u * m[2][0]) * (m[1][1] - v * m[2][1]) + (m[0][1] - u * m[2][1]) * (
                       -m[1][0] + v * m[2][0]))

        object_y = ((-m[0][3] + u * m[2][3]) * (-m[1][0] + v * m[2][0]) - (m[1][3] - v * m[2][3]) * (
            m[0][0] - u * m[2][0])) / \
                   ((m[0][0] - u * m[2][0]) * (m[1][1] - v * m[2][1]) + (m[0][1] - u * m[2][1]) * (
                       -m[1][0] + v * m[2][0]))

        return np.array([
            object_x,
            object_y,
            0
        ], dtype=float).tolist()

    def describe(self):
        return {
            "intrinsic_parameters": self.intrinsic_parameters.tolist(),
            "extrinsic_parameters": self.extrinsic_parameters.tolist(),
            "camera_matrix": self.camera_matrix.tolist(),
            "rotation_matrix": self.rotation_matrix.tolist(),
            "translation_vector": self.translation_vector.tolist(),
            "origin_image_coordinates": self.origin.tolist()
        }
