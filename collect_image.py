import cv2

if __name__ == '__main__':

    cap = cv2.VideoCapture(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1200)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
    cap.set(cv2.CAP_PROP_FPS, 15)

    index = 0

    while cap.isOpened():
        ret, image = cap.read()

        cv2.imshow("Image", image)

        key = cv2.waitKey(1)

        if key == ord('s'):
            cv2.imwrite('./calibration/image{}.jpg'.format(index), image)
            index += 1
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
