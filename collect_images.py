import os
from datetime import datetime

import cv2

from detector.robotdetector import RobotDetector
from src.infrastructure.camera import JSONCameraModelRepository

if __name__ == '__main__':
    cap = cv2.VideoCapture(1)

    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FPS, 15)

    print("FPS: {}".format(cap.get(cv2.CAP_PROP_FPS)))
    print("HEIGHT: {}".format(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    print("WIDTH: {}".format(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))

    now = datetime.utcnow().isoformat()
    calibration_session_dir = './data/calibrations/' + now

    os.mkdir(calibration_session_dir)

    camera_repository = JSONCameraModelRepository('./camera_model.json')
    camera_model = camera_repository.get_camera_model_by_id(0)
    origin = camera_model.get_origin()[0]

    index = 20

    robot_detector = RobotDetector()

    while cap.isOpened():
        ret, frame = cap.read()

        frame = camera_model.undistort_image(frame)

        position = robot_detector.detect_position(frame)

        try:
            center = position['center']
            radius = position['radius']

            world_position = camera_model.compute_image_to_world_coordinates(center[0], center[1], 10)

            print("Robot Position: {0}".format(world_position))

            cv2.circle(frame, center, radius, (0, 255, 0), 2)
            cv2.circle(frame, center, 2, (0, 0, 0), -1)
        except KeyError:
            continue

        cv2.circle(frame, (int(origin[0]), int(origin[1])), 2, (0, 255, 0), 2)

        if ret:
            cv2.imshow('frame', frame)

            key = cv2.waitKey(1)

            if key == ord('s'):
                print('Writing image')
                filename = "./image" + str(index) + '.jpg'
                index += 1
                print(filename)
                cv2.imwrite(filename, frame)

            elif key == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
