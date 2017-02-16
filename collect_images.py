import cv2

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FPS, 15)

    print("FPS: {}".format(cap.get(cv2.CAP_PROP_FPS)))
    print("HEIGHT: {}".format(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    print("WIDTH: {}".format(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))

    index = 0

    while cap.isOpened():
        ret, frame = cap.read()

        if ret:

            cv2.imshow('frame', frame)

            key = cv2.waitKey(1)

            if key == ord('s'):
                print('Writing image')
                filename = './data/images/hd/image' + str(index) + '.jpg'
                index += 1
                print(filename)
                cv2.imwrite(filename, frame)

            elif key == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
