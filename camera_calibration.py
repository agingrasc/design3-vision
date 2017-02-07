import numpy as np
import cv2
import glob

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6 * 9, 3), np.float32)
objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.
gray_image = None

def find_chessboard(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    has_corners, corners = cv2.findChessboardCorners(gray, (9, 6), None)

    if has_corners:
        objpoints.append(objp)

        cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), criteria)
        imgpoints.append(corners)

        frame = cv2.drawChessboardCorners(frame, (9, 6), corners, has_corners)


    return frame

def calibrate_from_pictures():
    images = glob.glob('calibration/*.jpg')

    for image_filename in images:
        image = cv2.imread(image_filename)

        image = find_chessboard(image)

        cv2.imshow("Image", image)
        cv2.waitKey(100)

def calibrate_from_video_capture():
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        has_frame, frame = cap.read()

        if has_frame:
            frame = find_chessboard(frame)

            cv2.imshow('Image', frame)
            key = cv2.waitKey(1)

            if key == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # calibrate_from_video_capture()

    calibrate_from_pictures()
    
    image = cv2.imread("./calibration/image0.jpg")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, image.shape[::-1], None, None)

    #undistorted = cv2.undistort(image, mtx, dist)

    #cv2.imshow("Undistored", undistorted)
    #cv2.waitKey()