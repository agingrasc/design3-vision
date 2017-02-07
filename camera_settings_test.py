import cv2




fps = 15
contrast = 0.1
saturation = 0.3
auto_gain = False
auto_exposure = False

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_GAIN, auto_gain)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, auto_exposure)
    cap.set(cv2.CAP_PROP_FPS, fps)
    cap.set(cv2.CAP_PROP_CONTRAST, contrast)
    cap.set(cv2.CAP_PROP_SATURATION, saturation)

    while True:
        has_frame, frame = cap.read()

        if has_frame:
            
            cv2.imshow('Setting app', frame)

            key = cv2.waitKey(1)

            if key == ord('q'):
                break

            elif key == ord('c'):
                contrast += 0.01
                cap.set(cv2.CAP_PROP_CONTRAST, contrast)
                print("Contrast: {}".format(cap.get(cv2.CAP_PROP_CONTRAST)))
            elif key == ord('v'):
                contrast -= 0.01
                cap.set(cv2.CAP_PROP_CONTRAST, contrast)
                print("Contrast: {}".format(cap.get(cv2.CAP_PROP_CONTRAST)))

            elif key == ord('s'):
                saturation += 0.01
                cap.set(cv2.CAP_PROP_SATURATION, saturation)
                print("Saturation: {}".format(cap.get(cv2.CAP_PROP_SATURATION)))
            elif key == ord('d'):
                saturation -= 0.01
                cap.set(cv2.CAP_PROP_SATURATION, saturation)
                print("Saturation: {}".format(cap.get(cv2.CAP_PROP_SATURATION)))

    cap.release()
    cv2.destroyAllWindows()
