import cv2
import json
import numpy as np

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


class Calibration:
    def __init__(self, camera_factory):
        self.camera_factory = camera_factory
        self.calibration_images = []
        self.target_points = []
        self.target_image_points = []
        self.target_object_points = []
        self.reference_image_index = 0

    def add_target_points(self, target_points):
        self.target_points = target_points

    def add_image(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        has_corners, corners = cv2.findChessboardCorners(image, (9, 6), None)
        if has_corners:
            self.target_object_points.append(self.target_points)
            self.calibration_images.append(image)

            corners = cv2.cornerSubPix(image, corners, (5, 5), (-1, -1), criteria)
            self.target_image_points.append(corners)

    def do_calibration(self):
        (
            ret,
            intrinsic_parameters,
            distortion_coefficients,
            rotation_vectors,
            translation_vectors
        ) = self.get_calibration_parameters(self.reference_image_index)

        return self.camera_factory.create_camera_model(
            intrinsic_parameters,
            translation_vectors[self.reference_image_index],
            rotation_vectors[self.reference_image_index],
            distortion_coefficients,
            self.target_image_points[0][0]
        )

    def get_calibration_parameters(self, calibration_image_index):
        return cv2.calibrateCamera(
            self.target_object_points,
            self.target_image_points,
            self.calibration_images[calibration_image_index].shape[::-1],
            None, None
        )


class CameraFactory:
    def create_camera_model(self, intrinsic_parameters, translation_vector, rotation_vector,
                            distortion_coefficients, origin):
        rotation_matrix = self.get_rotation_matrix_from(rotation_vector)
        extrinsic_parameters = np.concatenate((rotation_matrix, translation_vector), axis=1)
        camera_matrix = self.compute_camera_matrix(intrinsic_parameters, extrinsic_parameters)

        return CameraModel(
            intrinsic_parameters,
            extrinsic_parameters,
            camera_matrix,
            distortion_coefficients,
            rotation_matrix,
            translation_vector,
            origin)

    def get_rotation_matrix_from(self, rotation_vector):
        rotation_matrix, jacobian = cv2.Rodrigues(rotation_vector)
        return rotation_matrix

    def compute_camera_matrix(self, intrinsic_parameters, extrinsic_parameters):
        return np.dot(intrinsic_parameters, extrinsic_parameters)


class CameraModel:
    def __init__(self, intrinsic_parameters, extrinsic_parameters, camera_matrix,
                 distortion_coefficients, rotation_matrix, translation_vector, origin):
        self.intrinsic_parameters = np.array(intrinsic_parameters)
        self.extrinsic_parameters = np.array(extrinsic_parameters)
        self.camera_matrix = np.array(camera_matrix)
        self.distortion_coefficients = np.array(distortion_coefficients)
        self.rotation_matrix = np.array(rotation_matrix)
        self.translation_vector = np.array(translation_vector)
        self.origin = origin

    def compute_image_to_world_coordinates(self, u, v, d):
        m = self.camera_matrix
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

    def undistort_image(self, image):
        return cv2.undistort(image, self.intrinsic_parameters, self.distortion_coefficients, None, None)

    def describe(self):
        return {
            "intrinsic_parameters": self.intrinsic_parameters.tolist(),
            "extrinsic_parameters": self.extrinsic_parameters.tolist(),
            "camera_matrix": self.camera_matrix.tolist(),
            "rotation_matrix": self.rotation_matrix.tolist(),
            "translation_vector": self.translation_vector.tolist(),
            "distortion_coefficients": self.distortion_coefficients.tolist(),
            "origin_image_coordinates": self.origin.tolist()
        }
