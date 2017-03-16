import cv2

from detector.worldelement.robotdetector import RobotDetector, get_robot_angle
from infrastructure.camera import JSONCameraModelRepository

fps = 5
contrast = 0.1
saturation = 0.3
auto_gain = False
auto_exposure = False

DEFAULT_CAMERA_INDEX = 1

camera_repository = JSONCameraModelRepository('./data/camera_models/camera_models.json')
camera_model = camera_repository.get_camera_model_by_id(0)
origin = camera_model.get_origin()[0]

robot_detector = RobotDetector()


def process_image(frame):
    frame = camera_model.undistort_image(frame)
    try:
        robot_position = robot_detector.detect(frame)
        center = robot_position['robot_center']

        world_position = camera_model.compute_image_to_world_coordinates(center[0], center[1], 5)

        degrees = get_robot_angle(robot_position)

        cv2.circle(frame, robot_position['robot_center'], 1, (0, 0, 0), 2)
        cv2.line(frame, tuple(robot_position['direction'][0]), tuple(robot_position['direction'][1]), (0, 255, 0), 2)
        cv2.arrowedLine(frame, (0, 0), (50, 0), (0, 255, 0), 3)
        cv2.putText(frame, str(degrees), tuple(robot_position['direction'][1]), fontFace=cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1.0, color=(0, 0, 0))
        cv2.putText(frame, str([world_position[0], world_position[1]]), tuple(center), fontFace=cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1.5, color=(0, 0, 0))
    except Exception as e:
        print(e)
    cv2.circle(frame, (int(origin[0]), int(origin[1])), 2, (0, 255, 0), 2)
    return frame


def init_video_capture():
    capture = cv2.VideoCapture(DEFAULT_CAMERA_INDEX)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
    capture.set(cv2.CAP_PROP_GAIN, auto_gain)
    capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, auto_exposure)
    capture.set(cv2.CAP_PROP_CONTRAST, contrast)
    capture.set(cv2.CAP_PROP_SATURATION, saturation)
    return capture


index = 153

if __name__ == "__main__":
    cap = init_video_capture()

    while True:
        has_frame, frame = cap.read()

        if has_frame:
            # frame = process_image(frame)
            cv2.imshow('Setting app', frame)

            key = cv2.waitKey(1)

            if key == ord('q'):
                break

            if key == ord('s'):
                cv2.imwrite('./data/images/raw/image{}.jpg'.format(index), frame)
                index += 1
                print("Image saved")


    cap.release()
    cv2.destroyAllWindows()
