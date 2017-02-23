import json

from camera.camera import CameraModel

if __name__ == '__main__':
    with open('./config/camera_model.json') as file:
        camera_parameters = json.load(file)

    camera = CameraModel(None, None, camera_parameters['camera_matrix'], None, None, None, None)

    p1 = camera.compute_image_to_world_coordinates(324.5, 294, 8.72)
    p2 = camera.compute_image_to_world_coordinates(324.5, 294, 0)

    print(p1)
    print(p2)
