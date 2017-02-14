import os

from camera.camera import Camera

if __name__ == '__main__':
    camera = Camera()
    camera.load(os.path.abspath('./config/camera_matrix.json'))

    x1 = 71
    y1 = 129

    p1 = camera.compute_image_to_world_coordinate(x1, y1, 0)

    x2 = 248
    y2 = 128

    p2 = camera.compute_image_to_world_coordinate(x2, y2, 0)

    print(p2[0] - p1[0])
    print(p2[1] - p1[1])
