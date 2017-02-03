import cv2

cap = cv2.VideoCapture(0)

gain = False
cap.set(cv2.CAP_PROP_GAIN, gain)

fps = 10
cap.set(cv2.CAP_PROP_FPS, fps)

contrast = 0.1
cap.set(cv2.CAP_PROP_CONTRAST, contrast)

saturation = 0.3
cap.set(cv2.CAP_PROP_SATURATION, saturation)

exposure = 0.2
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
cap.set(cv2.CAP_PROP_EXPOSURE, exposure)

while True:
    ret, frame = cap.read()

    if ret == True:

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = frame

        cv2.imshow('frame', rgb)

        key = cv2.waitKey(1)

        if key == ord('x'):
            break


        elif key == ord('w'):
            fps += 5
            cap.set(cv2.CAP_PROP_FPS, fps)
            print("FPS: {}".format(cap.get(cv2.CAP_PROP_FPS)))
        elif key == ord('s'):
            fps -= 5
            cap.set(cv2.CAP_PROP_FPS, fps)
            print("FPS: {}".format(cap.get(cv2.CAP_PROP_FPS)))

        elif key == ord('d'):
            contrast += 0.01
            cap.set(cv2.CAP_PROP_CONTRAST, contrast)
            print(cap.get(cv2.CAP_PROP_CONTRAST))
        elif key == ord('a'):
            contrast -= 0.01
            cap.set(cv2.CAP_PROP_CONTRAST, contrast)
            print(cap.get(cv2.CAP_PROP_CONTRAST))

        elif key == ord('e'):
            saturation += 0.01
            cap.set(cv2.CAP_PROP_SATURATION, saturation)
            print(cap.get(cv2.CAP_PROP_SATURATION))
        elif key == ord('q'):
            saturation -= 0.01
            cap.set(cv2.CAP_PROP_SATURATION, saturation)
            print(cap.get(cv2.CAP_PROP_SATURATION))

        elif key == ord('z'):
            exposure += 0.01
            cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
            print(cap.get(cv2.CAP_PROP_EXPOSURE))
        elif key == ord('c'):
            exposure -= 0.01
            cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
            print(cap.get(cv2.CAP_PROP_EXPOSURE))

cap.release()
cv2.destroyAllWindows()
