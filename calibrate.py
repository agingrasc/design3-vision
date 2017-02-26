import glob
import cv2
import json

from src.camera.camera import CameraFactory
from src.service.calibrationservice import CalibrationService

if __name__ == '__main__':
    camera_factory = CameraFactory()
    calibration_service = CalibrationService(camera_factory)

    calibration_session_dir = "./data/calibrations/2017-02-25T18"

    images_path = glob.glob(calibration_session_dir + '/*.jpg')

    images = [cv2.imread(filename) for filename in images_path]

    camera_model = calibration_service.calibrate_from_images(images)
    camera_model["id"] = 0

    models = [camera_model]

    with open("./camera_model.json", 'w') as file:
        json.dump(models, file, indent=4)