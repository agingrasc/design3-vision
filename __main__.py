import base64
from tornado import websocket
import gzip
import tornado.ioloop
import json

import cv2

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 480)

class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def initialize(self):
        ret, frame = cam.read()
        self.str = base64.b64encode(frame)

    def open(self):
        print("WebSocket opened")
        self.write_message(self.str)

    def on_message(self, message):
        ret, frame = cam.read()
        if not ret:
            print("ERROR")
        cnt = cv2.imencode('.png', frame)[1]
        self.str = base64.b64encode(cnt)
        self.write_message(self.str)

    def on_close(self):
        print("WebSocket closed")

    def check_origin(self, origin):
        print(origin)
        return True


application = tornado.web.Application([(r"/", EchoWebSocket),])

if __name__ == "__main__":
    application.listen(3000)
    tornado.ioloop.IOLoop.instance().start()
