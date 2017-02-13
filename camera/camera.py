import cv2
import json
import numpy as np

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


class Camera:
    def __init__(self):
        self.target_points = []
        self.calibration_images = []
        self.target_object_points = []
        self.target_image_points = []
        self.camera_matrix = []
        self.intrinsic_parameters = []
        self.distortion = []
        self.rotation_matrix = []
        self.translation_vectors = []
        self.extrinsic_parameters = []
        self.reference_image = 0
        self.origin = []

    def load_camera_model(self, filepath):
        with open(filepath) as file:
            camera_parameters = json.load(file)
            self.camera_matrix = camera_parameters['camera_matrix']

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
            intrinsic_matrix,
            distortion_matrix,
            rotation_vectors,
            translation_vectors
        ) = self.get_calibration_parameters()

        rotation_matrix, jacobian = cv2.Rodrigues(rotation_vectors[0])

        self.intrinsic_parameters = intrinsic_matrix
        self.distortion = distortion_matrix
        self.rotation_matrix = rotation_matrix
        self.translation_vectors = translation_vectors
        self.extrinsic_parameters = np.concatenate((rotation_matrix, translation_vectors[0]), axis=1)

        self.camera_matrix = np.dot(self.intrinsic_parameters, self.extrinsic_parameters)

    def get_calibration_parameters(self):
        reference_image = self.calibration_images[0]
        self.reference_image = 0
        self.origin = self.target_image_points[0][0]
        return cv2.calibrateCamera(
            self.target_object_points, self.target_image_points, reference_image.shape[::-1], None, None)

    def undistort(self, image):
        return cv2.undistort(image, self.intrinsic_parameters, self.distortion, None, None)

    def compute_image_to_world_coordinate(self, u, v, z):
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
        ], dtype=float)
