import json
import numpy as np

def get_world_coordinate(x, y, z, camera_matrix):
    m = camera_matrix

    u = x
    v = y

    x = ((-m[0][3] + u * m[2][3]) * (m[1][1] - v * m[2][1]) - (m[1][3] - v * m[2][3]) * (-m[0][1] + u * m[2][1])) / \
        ((m[0][0] - u * m[2][0]) * (m[1][1] - v * m[2][1]) + (m[0][1] - u * m[2][1]) * (-m[1][0] + v * m[2][0]))

    y = ((-m[0][3] + u * m[2][3]) * (-m[1][0] + v * m[2][0]) - (m[1][3] - v * m[2][3]) * (m[0][0] - u * m[2][0])) / \
        ((m[0][0] - u * m[2][0]) * (m[1][1] - v * m[2][1]) + (m[0][1] - u * m[2][1]) * (-m[1][0] + v * m[2][0]))

    return np.array([
        x,
        y,
        0
    ], dtype=float)

if __name__ == '__main__':
    with open('./camera_parameters.json', 'r') as data:
        camera_parameters = json.load(data)

        intrinsic = np.array(camera_parameters['intrinsic'])
        distortion = np.array(camera_parameters['distortion'])
        rotation_matrix = np.array(camera_parameters['rotation_matrix'])
        translation_vector = np.array(camera_parameters['translation_vector'])

        extrinsic = np.concatenate((rotation_matrix, translation_vector), axis=1)

        origin = np.array([[0, 0, 0, 1]]).T

        camera = np.dot(intrinsic, extrinsic)

        camera_point = np.dot(camera, origin)

        x1 = 71
        y1 = 129

        p1 = get_world_coordinate(x1, y1, 0, camera)

        x2 = 248
        y2 = 128

        p2 = get_world_coordinate(x2, y2, 0, camera)

        print(p2[0] - p1[0])
        print(p2[1] - p1[1])