import glob
import json

import cv2

from service.camera.calibrationservice import CalibrationService
from src.camera.camera import CameraFactory

if __name__ == '__main__':
    camera_factory = CameraFactory()
    calibration_service = CalibrationService(camera_factory)

    calibration_session_dir = "./calibration"

    images_path = glob.glob(calibration_session_dir + '/*.jpg')

    images = [cv2.imread(filename) for filename in images_path]

    camera_model = calibration_service.calibrate_from_images(images)
    camera_model["id"] = 10

    models = [camera_model]

    with open("./camera_models.json", 'w') as file:
        json.dump(models, file, indent=4)