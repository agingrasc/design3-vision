import cv2
import numpy as np
import math

stop_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


class CalibrationTargetNotFoundError(Exception):
    pass


class Calibration:
    def __init__(self, camera_factory):
        self._camera_factory = camera_factory
        self._calibration_images = []
        self._target_points = []
        self._target_image_points = []
        self._target_object_points = []
        self._reference_image_index = 0

    def add_target_points(self, target_points):
        self._target_points = target_points

    def collect_target_image(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        has_target, corners = cv2.findChessboardCorners(image, (9, 6), None)
        if has_target:
            self._target_object_points.append(self._target_points)
            self._calibration_images.append(image)

            corners = cv2.cornerSubPix(image, corners, (5, 5), (-1, -1), stop_criteria)
            self._target_image_points.append(corners)
        else:
            raise CalibrationTargetNotFoundError

    def do_calibration(self):
        (
            ret,
            intrinsic_parameters,
            distortion_coefficients,
            rotation_vectors,
            translation_vectors
        ) = self._get_calibration_parameters(self._reference_image_index)

        return self._camera_factory.create_camera_model(
            intrinsic_parameters,
            translation_vectors[self._reference_image_index],
            rotation_vectors[self._reference_image_index],
            distortion_coefficients,
            self._target_image_points[0][0]
        )

    def _get_calibration_parameters(self, calibration_image_index):
        return cv2.calibrateCamera(
            self._target_object_points,
            self._target_image_points,
            self._calibration_images[calibration_image_index].shape[::-1],
            None, None
        )


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

    def create_calibration(self):
        calibration = Calibration(self)
        calibration.add_target_points(self.create_calibration_target_points())
        return calibration

    def create_calibration_target_points(self):
        object_points = np.zeros((6 * 9, 3), np.float32)
        object_points[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)
        return object_points

    def _get_rotation_matrix_from(self, rotation_vector):
        rotation_matrix, jacobian = cv2.Rodrigues(rotation_vector)
        return rotation_matrix

    def _get_extrinsic_parameters(self, rotation_matrix, translation_vector):
        return np.concatenate((rotation_matrix, translation_vector), axis=1)

    def _compute_camera_matrix(self, intrinsic_parameters, extrinsic_parameters):
        return np.dot(intrinsic_parameters, extrinsic_parameters)


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
        return self._origin

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


if __name__ == '__main__':
    camera_model = CameraModel(None, None, None, None, None, None, None, None)

    transform = camera_model.compute_transform_matrix(39, [73, 26])

    point = np.array([
        79,
        31,
        1
    ])

    print(transform)
    print(point)

    print(np.dot(transform, point))
