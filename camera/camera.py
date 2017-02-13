import cv2
import numpy as np

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


class Camera:
    def __init__(self):
        self.target_points = []
        self.calibration_images = []
        self.target_object_points = []
        self.target_image_points = []
        self.camera_matrix = []

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
        reference_image = self.calibration_images[0]

        ret, intrinsic_matrix, distortion_matrix, rotation_vectors, translation_vectors = cv2.calibrateCamera(
            self.target_object_points, self.target_image_points, reference_image.shape[::-1], None, None)
        rotation_matrix, jacobian = cv2.Rodrigues(rotation_vectors[0])

        self.intrinsic_parameters = intrinsic_matrix
        self.distortion = distortion_matrix
        self.rotations_vectors = rotation_vectors
        self.translation_vectors = translation_vectors

        self.camera_matrix = np.concatenate((rotation_matrix, translation_vectors[0]), axis=1)

    def undistort(self, image):
        return cv2.undistort(image, self.intrinsic_parameters, self.distortion, None, None)
