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

        # frame = cv2.drawChessboardCorners(frame, (9, 6), corners, has_corners)

    return frame


def calibrate_from_pictures():
    images = glob.glob('calibration/*.jpg')

    for image_filename in images:
        image = cv2.imread(image_filename)

        image = find_chessboard(image)

        # cv2.imshow("Image", image)
        # cv2.waitKey(1000)


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


def draw(img, corners, imgpts):
    imgpts = np.int32(imgpts).reshape(-1, 2)

    # draw ground floor in green
    img = cv2.drawContours(img, [imgpts[:4]], -1, (0, 255, 0), -3)

    # draw pillars in blue color
    for i, j in zip(range(4), range(4, 8)):
        img = cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]), (255), 3)

    # draw top layer in red color
    img = cv2.drawContours(img, [imgpts[4:]], -1, (0, 0, 255), 3)

    return img

def build_square_tower(x, y, height):
    size = 3

    return np.float32([[x, y, 0],
                       [x, y + size, 0],
                       [x + size, y + size, 0],
                       [x + size, y, 0],

                       [x, y, -height],
                       [x, y + size, -height],
                       [x + size, y + size, -height],
                       [x + size, y, -height]])

if __name__ == "__main__":
    # calibrate_from_video_capture()

    calibrate_from_pictures()

    axis = build_square_tower(0, 0, 4)

    image = cv2.imread("./calibration/image1.jpg")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    has_corners, corners = cv2.findChessboardCorners(image, (9, 6), None)
    corners2 = cv2.cornerSubPix(image, corners, (5, 5), (-1, -1), criteria)

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, image.shape[::-1], None, None)

    imgpts, jac = cv2.projectPoints(axis, np.array(rvecs[1]), np.array(tvecs[1]), mtx, dist)

    image = cv2.imread('./calibration/image9.jpg')

    img = draw(image, corners2, imgpts)

    cv2.imshow('Pose', img)
    cv2.waitKey()
