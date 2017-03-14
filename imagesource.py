import cv2


class VideoImageSource:
    def __init__(self):
        self._video_capture = cv2.VideoCapture(1)
        self._video_capture.set(cv2.CAP_PROP_FPS, 15)

    def start(self):
        while self._video_capture.isOpened():
            ret, image = self._video_capture.read()

            if ret:
                cv2.imshow("image", image)
                cv2.waitKey(1)


if __name__ == '__main__':
    video = VideoImageSource()

    video.start()
