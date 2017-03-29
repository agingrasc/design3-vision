import numpy as np
from math import acos

import config
from detector.worldelement.obstaclepositiondetector import Obstacle
from geometry.coordinate import Coordinate
from world.drawingarea import DrawingArea
from world.robot import Robot
from world.table import Table
from world.world import World


class ImageToWorldTranslator:
    def __init__(self, camera_model, image_detection_service):
        self._camera_model = camera_model
        self._image_detection_service = image_detection_service
        self._world = None
        self._robot = None
        self._obstacles = None
        self._drawing_area = None

    def translate_image_to_world(self, image):
        image_elements = self._image_detection_service.detect_all_world_elements(image)

        for image_element in image_elements:
            if isinstance(image_element, Table):
                self._world = self._translate_table_to_world(image_element)

            elif isinstance(image_element, DrawingArea):
                inner_square_dimension = self._get_world_inner_square_dimension(image_element)
                image_element.set_inner_square_dimension(inner_square_dimension)
                self._drawing_area = image_element

            elif isinstance(image_element, Robot):
                if self._robot is None:
                    self._robot = self._compute_and_set_projected_coordinates(image_element)
                else:
                    self._robot = self._compute_and_set_projected_coordinates(image_element)

            elif isinstance(image_element, list):
                self._obstacles = [self._adjust_obstacle_position(obstacle) for obstacle in image_element]

        if self._robot and self._world is not None:
            robot_target_to_world_in_mm = self._transform_target_to_world(self._world._target_to_world,
                                                                          self._robot._world_position)
            self._robot.set_world_position(robot_target_to_world_in_mm)

        if self._obstacles and self._world is not None:
            world_obstacles = []

            for obstacle in self._obstacles:
                obstacle_target_to_world_in_mm = self._transform_target_to_world(self._world._target_to_world,
                                                                                 obstacle._world_position)
                obstacle.set_world_position(obstacle_target_to_world_in_mm)
                world_obstacles.append(obstacle)

            self._obstacles = world_obstacles

        return self._world, self._robot, image_elements

    def get_obstacles(self):
        return self._obstacles

    def get_world(self):
        return self._world

    def transform_segments(self, segmented_image, segments, scaling_factor):
        segmented_image_width = segmented_image.shape[0]
        drawing_area = self._drawing_area

        drawing_area_center = np.array(drawing_area._inner_square._center)
        drawing_area_inner = drawing_area._inner_square.as_coordinates()

        drawing_area_inner_width = drawing_area_inner[1].distance_from(drawing_area_inner[0])
        scaling = drawing_area_inner_width / segmented_image_width * scaling_factor

        segmented_image_center = np.array([segmented_image_width / 2 * scaling, segmented_image_width / 2 * scaling])
        translation = (drawing_area_center - segmented_image_center).tolist()

        scale_matrix = np.array([
            [scaling, 0, 0],
            [0, scaling, 0],
            [0, 0, 1]
        ])

        segments = np.array([np.dot(scale_matrix, np.array([p[0], p[1], 1])) for p in segments[:, 0].tolist()])
        transform_matrix = np.array([
            [1, 0, translation[0]],
            [0, 1, translation[1]],
            [0, 0, 1]
        ])

        segments = [np.dot(transform_matrix, np.array([p[0], p[1], 1])).astype('int').tolist()[0:2] for p in
                    segments]

        world_segments = [self._camera_model.compute_image_to_world_coordinates(p[0], p[1], 0) for p in segments]
        world_segments = [[p[0], p[1]] for p in world_segments]

        world_segments = [self._transform_target_to_world(self._world._target_to_world, np.array(p)) for p in
                          world_segments]
        return segments, world_segments

    def _compute_world_transform_matrix(self, table, world_origin):
        x_axis = np.array([world_origin, table._rectangle.as_contour_points().tolist()[1]])
        x_axis = [np.array(self._camera_model.compute_image_to_world_coordinates(point[0], point[1], 0)) for point in
                  x_axis]

        v1 = x_axis[0]
        v2 = x_axis[1]

        x_axis = v2 - v1
        x_axis = x_axis[0:2]

        origin_x_axis = np.array([5, 0])

        angle = acos(np.dot(origin_x_axis, x_axis) / (np.linalg.norm(origin_x_axis) * np.linalg.norm(x_axis)))

        v1[2] = 0.

        target_to_world = self._camera_model.compute_transform_matrix(np.rad2deg(angle), v1)
        return target_to_world

    def _compute_and_set_projected_coordinates(self, robot):
        target_coordinates = self._transform_image_to_target(robot)
        robot.set_world_position(target_coordinates)

        adjusted_image_coordinates = self._camera_model.compute_world_to_image_coordinates(target_coordinates[0],
                                                                                           target_coordinates[1], 0)
        robot.set_image_position(adjusted_image_coordinates)
        return robot

    def _translate_table_to_world(self, table):
        image_corners = np.round(table._rectangle.as_contour_points()).astype('int')
        table_corners = self._convert_image_points_to_world_coordinates(image_corners)
        table_dimensions = self._get_element_dimension(table_corners)
        world_origin = table._rectangle.as_contour_points().tolist()[0]
        target_to_world = self._compute_world_transform_matrix(table, world_origin)

        return World(table_dimensions['width'], table_dimensions['length'],
                     world_origin[0], world_origin[1],
                     target_to_world)

    def _get_world_inner_square_dimension(self, drawing_area):
        image_corners = np.round(drawing_area._inner_square.as_contour_points()).astype('int')
        inner_square_corners = self._convert_image_points_to_world_coordinates(image_corners)
        inner_dimension = self._get_element_dimension(inner_square_corners)
        return inner_dimension

    def _transform_image_to_target(self, robot):
        image_x, image_y = robot._image_position
        target_coordinates = self._camera_model.compute_image_to_world_coordinates(image_x, image_y,
                                                                                   config.ROBOT_HEIGHT_IN_TARGET_UNIT)
        return target_coordinates

    def _transform_target_to_world(self, target_to_world_matrix, target_coordinates):
        world_position = self._camera_model.transform_coordinates(target_to_world_matrix, target_coordinates)

        world_position_in_mm = [
            world_position[0] * config.TARGET_SIDE_LENGTH,
            world_position[1] * config.TARGET_SIDE_LENGTH
        ]

        return world_position_in_mm

    def _adjust_obstacle_position(self, obstacle):
        target_coordinates = self._camera_model.compute_image_to_world_coordinates(obstacle._position[0],
                                                                                   obstacle._position[1],
                                                                                   10)
        obstacle.set_world_position(target_coordinates)

        adjusted_position = self._camera_model.compute_world_to_image_coordinates(target_coordinates[0],
                                                                                  target_coordinates[1], 0)
        obstacle.set_position(adjusted_position)
        return obstacle

    def _convert_image_points_to_world_coordinates(self, image_corners):
        table_corners = [self._camera_model.compute_image_to_world_coordinates(corner[0], corner[1], 0) for corner in
                         image_corners.tolist()]
        return self._to_coordinates(table_corners)

    def _to_coordinates(self, points):
        return [Coordinate(point[0], point[1]) for point in points]

    def _get_element_dimension(self, corners):
        sides = self._get_table_dimensions(corners)
        return {
            "length": sides[0],
            "width": sides[3]
        }

    def _get_table_dimensions(self, table_corners):
        return sorted([table_corners[0].distance_from(table_corners[1]) * 4.4,
                       table_corners[1].distance_from(table_corners[2]) * 4.4,
                       table_corners[2].distance_from(table_corners[3]) * 4.4,
                       table_corners[3].distance_from(table_corners[0]) * 4.4])

    def translate_path(self, path):
        if self._world:
            translate_matrix = self._camera_model.compute_transform_matrix(0, [self._world._image_origin._x,
                                                                               self._world._image_origin._y])

            image_path = [self._camera_model.transform_coordinates(translate_matrix, point) for point in path]

            return image_path
        else:
            return []
