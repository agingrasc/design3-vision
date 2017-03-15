import cv2
import numpy as np

import config
from infrastructure.camera import JSONCameraModelRepository


def angle_cos(p0, p1, p2):
    d1, d2 = (p0 - p1).astype('float'), (p2 - p1).astype('float')
    return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1) * np.dot(d2, d2)))


if __name__ == '__main__':
    camera_model_repository = JSONCameraModelRepository(config.CAMERA_MODELS_FILE_PATH)
    camera_model = camera_model_repository.get_camera_model_by_id(config.TABLE_CAMERA_MODEL_ID)

    x_axis, target_origin, y_axis = camera_model.get_origin_orthogonal()
    cv2.circle(image, target_origin, 1, (0, 0, 255), 2)
    cv2.arrowedLine(image, target_origin, x_axis, (0, 0, 255), 2)
    cv2.arrowedLine(image, target_origin, y_axis, (0, 0, 255), 2)

    image = cv2.imread('../data/images/full_scene/image10.jpg')

    image = camera_model.undistort_image(image)



    cv2.imshow('Image', image)
    cv2.waitKey()
