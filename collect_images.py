import base64
import gzip

import cv2
import numpy as np
import requests
import tornado
from tornado import websocket

from detector.worldelement.robotpositiondetector import get_robot_angle

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
cap.set(cv2.CAP_PROP_FPS, 15)

print("FPS: {}".format(cap.get(cv2.CAP_PROP_FPS)))
print("HEIGHT: {}".format(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
print("WIDTH: {}".format(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))


ret, frame = cap.read()


def process_image(frame):
    frame = camera_model.undistort_image(frame)
    try:
        robot_position = robot_detector.detect_position(frame)
        center = robot_position['robot_center']

        # world_position = camera_model.compute_image_to_world_coordinates(center[0], center[1], 10)

        world_position = requests.post("http://localhost:5000/world_coordinates",
                                       json={"x": center[0], "y": center[1], "z": -10}).json()
        print(world_position)
        print("Robot Position: {0}".format(world_position))

        degrees = get_robot_angle(robot_position)

        cv2.circle(frame, robot_position['robot_center'], 1, (0, 0, 0), 2)
        cv2.line(frame, tuple(robot_position['direction'][0]), tuple(robot_position['direction'][1]), (0, 255, 0),
                 2)
        cv2.arrowedLine(frame, (0, 0), (50, 0), (0, 255, 0), 3)
        cv2.putText(frame, str(degrees), tuple(robot_position['direction'][1]), fontFace=cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1.0, color=(255, 255, 255))
    except Exception as e:
        print(e)
    cv2.circle(frame, (int(origin[0]), int(origin[1])), 2, (0, 255, 0), 2)
    return frame, robot_position


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def initialize(self):
        ret, frame = cap.read()
        frame, world_coordinate = process_image(frame)
        self.str = base64.b64encode(frame)

    def open(self):
        print("WebSocket opened")
        self.write_message(self.str)

    def on_message(self, message):
        ret, frame = cap.read()
        if not ret:
            print("ERROR")
        frame, world_position = process_image(frame)

        direction = [world_position['direction'][0], tuple(world_position['direction'][1])]

        direction = np.array(direction, dtype=int).tolist()


        body = {
            "center": world_position['robot_center'],
            "direction": get_robot_angle(world_position)
        }

        req = requests.post("http://localhost:5000/set_robot_position", json=body).json()

        image = cv2.imencode('.png', frame)[1]
        self.str = base64.b64encode(image)

        self.write_message(gzip.compress(image))

    def on_close(self):
        print("WebSocket closed")

    def check_origin(self, origin):
        print(origin)
        return True


if __name__ == '__main__':
    application = tornado.web.Application([(r"/", EchoWebSocket), ])
    application.listen(3000)
    tornado.ioloop.IOLoop.instance().start()

    cap.release()
    cv2.destroyAllWindows()
