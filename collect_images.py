import cv2
import os

cap = cv2.VideoCapture(1)

cap.set(cv2.CAP_PROP_FPS, 15)
print("FPS: {}".format(cap.get(cv2.CAP_PROP_FPS)))

raw_dir = os.listdir('./raw')

index = 0

while True:
    ret, frame = cap.read()

    if ret == True:
        cv2.imshow('frame', frame)

        key = cv2.waitKey(1)

        if key == ord('s'):
            print('Writing image')
            filename = 'calibration/image' + str(index) + '.jpg'
            index += 1
            print(filename)
            cv2.imwrite(filename, frame)

        elif key == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
