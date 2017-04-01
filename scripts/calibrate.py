import datetime
import glob
import json
import cv2

from camera.camerafactory import CameraFactory
from camera.calibration import CalibrationTargetNotFoundError
from service.camera.calibrationservice import CalibrationService


def calibrate_from_video_capture(calibration_service, camera_factory):
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1200)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
    cap.set(cv2.CAP_PROP_FPS, 15)

    images = 0

    calibration = calibration_service.create_calibration((6, 4))

    while images != 20 and cap.isOpened():
        ret, image = cap.read()

        if ret:
            cv2.imshow('Calibration', image)
            key = cv2.waitKey(1)

            if key == ord('s'):
                try:
                    print('Adding image {}'.format(images))
                    calibration.collect_target_image(image)
                    images += 1
                    print(images)
                except CalibrationTargetNotFoundError as e:
                    print(type(e).__name__)
                    pass
            elif key == ord('q'):
                print('Aborting calibration session...')
                cap.release()
                cv2.destroyAllWindows()
                exit(0)

    camera_model = calibration.do_calibration()
    return camera_model


if __name__ == '__main__':
    camera_factory = CameraFactory()
    calibration_service = CalibrationService(camera_factory)
    now = datetime.datetime.now()
    print('New calibration {}'.format(now))

    # camera_model = calibrate_from_video_capture()

    images = [cv2.imread(filename) for filename in glob.glob('../data/images/calibrations/2017-02-25-1/*.jpg')]
    camera_model = calibration_service.calibrate_from_images((9, 6), images)

    camera_model_dto = camera_factory.create_camera_model_dto(camera_model)
    models = [camera_model_dto]

    with open("./camera_models.json", 'w') as file:
        json.dump(models, file, indent=4)
