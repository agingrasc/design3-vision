import cv2
import numpy as np

STOP_CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


class CalibrationTargetNotFoundError(Exception):
    pass


class Calibration:
    def __init__(self, target_shape, camera_factory):
        self._target_shape = target_shape
        self._camera_factory = camera_factory
        self._calibration_images = []
        self._target_image_points = []
        self._target_object_points = []
        self._reference_image_id = 0
        self._target_points = self._init_calibration_target_points()

    def collect_target_image(self, image):
        has_target, corners = cv2.findChessboardCorners(image, self._target_shape)

        if has_target:
            corners = cv2.cornerSubPix(image, corners, (5, 5), (-1, -1), STOP_CRITERIA)
            self._target_image_points.append(corners)
            self._target_object_points.append(self._target_points)
            self._calibration_images.append(image)
            cv2.drawChessboardCorners(image, self._target_shape, corners, has_target)
            cv2.imshow('Target', image)
        else:
            raise CalibrationTargetNotFoundError

    def has_target_shape(self, target_shape):
        return self._target_shape[0] == target_shape[0] and self._target_shape[1] == target_shape[1]

    def do_calibration(self):
        (
            ret,
            intrinsic_parameters,
            distortion_coefficients,
            rotation_vectors,
            translation_vectors
        ) = self._init_calibration_parameters_from(self._reference_image_id)

        return self._camera_factory.create_camera_model(
            intrinsic_parameters,
            translation_vectors[self._reference_image_id],
            rotation_vectors[self._reference_image_id],
            distortion_coefficients,
            self._target_image_points[0][0]
        )

    def _init_calibration_parameters_from(self, image_id):
        return cv2.calibrateCamera(
            self._target_object_points,
            self._target_image_points,
            self._calibration_images[image_id].shape[::-1],
            None, None
        )

    def _init_calibration_target_points(self):
        total_grid_cells = self._target_shape[0] * self._target_shape[1]
        object_points = np.zeros((total_grid_cells, 3), np.float32)
        object_points[:, :2] = np.mgrid[0:self._target_shape[0], 0:self._target_shape[1]].T.reshape(-1, 2)
        return object_points
