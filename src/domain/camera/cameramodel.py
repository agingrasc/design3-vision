import cv2

from numpy import cross, dot, array


class CameraModel:
    def __init__(self, id, intrinsic_parameters, extrinsic_parameters, camera_matrix,
                 distortion_coefficients, rotation_matrix, translation_vector, origin):
        self._id = id
        self._intrinsic_parameters = array(intrinsic_parameters)
        self._extrinsic_parameters = array(extrinsic_parameters)
        self._camera_matrix = array(camera_matrix)
        self._distortion_coefficients = array(distortion_coefficients)
        self._rotation_matrix = array(rotation_matrix)
        self._translation_vector = array(translation_vector)
        self._target_origin = array(origin)

    def target_to_image_coordinates(self, u, v, d):
        homogeneous_coordinates = dot(self._camera_matrix, array([u, v, d, 1]))
        return array([
            homogeneous_coordinates[0] / homogeneous_coordinates[2],
            homogeneous_coordinates[1] / homogeneous_coordinates[2]
        ]).astype('int').tolist()

    def image_to_target_coordinates(self, u, v, d):
        m = self._camera_matrix
        A = array(m[0] - (u * m[2]))
        B = array(m[1] - (v * m[2]))

        u_1 = A[:3]
        d_1 = A[3]
        u_2 = B[:3]
        d_2 = B[3]
        u_3 = array([0, 0, 1])
        d_3 = d

        P = ((-d_1 * cross(u_2, u_3)) + (-d_2 * cross(u_3, u_1)) + (-d_3 * cross(u_1, u_2))) / \
            dot(u_1.T, cross(u_2, u_3))

        return array(P, dtype=float).tolist()

    def transform_coordinates(self, transform_matrix, coordinate):
        homogeneous_coordinate = array([
            coordinate[0],
            coordinate[1],
            1
        ])

        return self._homogeneous_to_cart(dot(transform_matrix, homogeneous_coordinate))

    def undistort_image(self, image):
        return cv2.undistort(image, self._intrinsic_parameters, self._distortion_coefficients, None, None)

    def get_id(self):
        return self._id

    def _homogeneous_to_cart(self, coordinate):
        return [
            coordinate[0] / coordinate[2],
            coordinate[1] / coordinate[2]
        ]
