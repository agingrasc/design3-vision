import numpy as np
import cv2
import glob
import json

from camera.camera import Camera

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.
gray_image = None


def create_object_points():
    object_points = np.zeros((6 * 9, 3), np.float32)
    object_points[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)
    return object_points


def find_chessboard(frame, object_points):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    has_corners, corners = cv2.findChessboardCorners(gray, (9, 6), None)

    if has_corners:
        objpoints.append(object_points)

        cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), criteria)
        imgpoints.append(corners)

        frame = cv2.drawChessboardCorners(frame, (9, 6), corners, has_corners)

    return frame


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
    # for i, j in zip(range(4), range(4, 8)):
    # img = cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]), (255), 3)

    # draw top layer in red color
    # img = cv2.drawContours(img, [imgpts[4:]], -1, (0, 0, 255), 3)

    return img


def build_cube(x, y, height):
    size = 12.8

    return np.float32([[x, y, 0],
                       [x, y + size, 0],
                       [x + size, y + size, 0],
                       [x + size, y, 0],

                       [x, y, -height],
                       [x, y + size, -height],
                       [x + size, y + size, -height],
                       [x + size, y, -height]])


def prepare_for_calibration(camera):
    camera.add_target_points(create_object_points())
    images = glob.glob('calibration/*.jpg')
    for image_filename in images:
        image = cv2.imread(image_filename)
        camera.add_image_for_calibration(image)


if __name__ == "__main__":
    camera = Camera()

    prepare_for_calibration(camera)

    camera.calibrate()

    camera_model = {
        "camera_matrix": camera.camera_matrix.tolist(),
        "reference_image_id": camera.reference_image,
        "origin_image_coordinates": camera.origin.tolist()
    }

    with open('./camera_matrix.json', 'w') as file:
        json.dump(camera_model, file, indent=4)

















    # for image_filename in glob.glob('./calibration/*.jpg'):
    #     image = camera.undistort(cv2.imread(image_filename))
    #
    #     print("Saving " + image_filename.split('/')[2])
    #     image_name = image_filename.split('/')[2]
    #     cv2.imwrite('./undistort/' + image_name, image)

        # cv2.imshow('Undistort', image)
        # cv2.waitKey(2000)

        # cube_object_points = build_cube(0, 0, 0)


        # ret, intrinsic_matrix, distortion_matrix, rotation_vectors, translation_vectors = cv2.calibrateCamera(
        #     objpoints, imgpoints, image.shape[::-1], None, None)
        #
        # rotation_matrix, jacobian = cv2.Rodrigues(rotation_vectors[0])
        #
        # image = cv2.imread('./calibration/image0.jpg')
        #
        # h, w = image.shape[:2]
        # newcameramtx, roi = cv2.getOptimalNewCameraMatrix(intrinsic_matrix, distortion_matrix, (w, h), 0, (w, h))
        #
        # image = cv2.undistort(image, intrinsic_matrix, distortion_matrix, None, None)
        #
        # cube_image_points, jacobian = cv2.projectPoints(
        #     cube_object_points,
        #     np.array(rotation_vectors[0]),
        #     np.array(translation_vectors[0]),
        #     intrinsic_matrix,
        #     distortion_matrix)
        #
        # camera_parameters = {
        #     "intrinsic": newcameramtx.tolist(),
        #     "distortion": distortion_matrix.tolist(),
        #     "rotation_matrix": rotation_matrix.tolist(),
        #     "translation_vector": np.array(translation_vectors[0]).tolist()
        # }
        #
        # with open('./camera_parameters.json', 'w') as outfile:
        #     json.dump(camera_parameters, outfile, indent=4)
        #
        # image = draw(image, corners2, cube_image_points)
        #
        # cv2.imshow('Pose', image)
        # cv2.waitKey()
