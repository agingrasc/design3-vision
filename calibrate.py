import datetime
import json
import cv2

from service.camera.calibrationservice import CalibrationService
from src.camera.camera import CameraFactory, CalibrationTargetNotFoundError

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1200)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
    cap.set(cv2.CAP_PROP_FPS, 15)

    images = []

    camera_factory = CameraFactory()
    calibration_service = CalibrationService(camera_factory)

    now = datetime.datetime.now()
    print('New calibration {}'.format(now))
    calibration = calibration_service.create_calibration()

    while len(images) < 10 and cap.isOpened():
        ret, image = cap.read()

        if ret:
            cv2.imshow('Calibration', image)
            key = cv2.waitKey(1)

            if key == ord('s'):
                try:
                    print('Adding image')
                    calibration.collect_target_image(image)
                except CalibrationTargetNotFoundError as e:
                    print(type(e).__name__)
                    continue
            elif key == ord('q'):
                print('Aborting calibration session...')
                cap.release()
                cv2.destroyAllWindows()
                exit(0)

    camera_model = calibration.do_calibration()

    camera_model["id"] = 10
    models = [camera_model]

    with open("./camera_models.json", 'w') as file:
        json.dump(models, file, indent=4)
