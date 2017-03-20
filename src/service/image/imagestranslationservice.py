from math import acos

import numpy as np

from config import ROBOT_HEIGHT_IN_TARGET_UNIT
from geometry.coordinate import Coordinate
from world.robot import Robot
from world.table import Table
from world.world import World


class ImageToWorldTranslator:
    def __init__(self, camera_model, image_detection_service):
        self._camera_model = camera_model
        self._image_detection_service = image_detection_service

    def translate_image_to_world(self, image):
        world = None
        robot = None
        world_elements = self._image_detection_service.detect_all_world_elements(image)

        for image_element in world_elements:
            if isinstance(image_element, Table):
                world = self._create_world(image_element)
            elif isinstance(image_element, Robot):
                robot = self._adjust_robot_position(image_element)
            elif isinstance(image_element, list):
                for obstacle in image_element:
                    obstacle = self._adjust_obstacle_position(obstacle)

        for element in world_elements:
            if isinstance(element, list):
                for obstacle in element:
                    obstacle.draw_in(image)
            else:
                element.draw_in(image)

        if robot and world is not None:
            robot.set_world_position(self._convert_target_to_world(world, robot))
        return world, robot

    def _create_world(self, table):
        table_corners = self._convert_table_image_points_to_world_coordinates(table)
        table_dimensions = self._get_table_dimension(table_corners)
        world_origin = table._rectangle.as_contour_points().tolist()[0]

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

        return World(table_dimensions['width'], table_dimensions['length'], world_origin[0], world_origin[1],
                     target_to_world)

    def _adjust_obstacle_position(self, obstacle):
        world_position = self._camera_model.compute_image_to_world_coordinates(obstacle._position[0],
                                                                               obstacle._position[1],
                                                                               10)

        adjusted_position = self._camera_model.compute_world_to_image_coordinates(world_position[0],
                                                                                  world_position[1], 0)
        obstacle.set_position(adjusted_position)
        return obstacle

    def _adjust_robot_position(self, robot):
        world_position = self._camera_model.compute_image_to_world_coordinates(robot._position[0],
                                                                               robot._position[1],
                                                                               ROBOT_HEIGHT_IN_TARGET_UNIT)
        robot.set_world_position(world_position)

        adjusted_position = self._camera_model.compute_world_to_image_coordinates(world_position[0],
                                                                                  world_position[1], 0)
        robot.set_position(adjusted_position)
        return robot

    def _convert_target_to_world(self, world, robot):
        robot_target_position = np.array([
            robot._world_position[0],
            robot._world_position[1],
            1
        ])
        return self._homogeneous_to_cart(np.dot(world._target_to_world, robot_target_position))

    def _homogeneous_to_cart(self, coordinate):
        return [
            coordinate[0] / coordinate[2],
            coordinate[1] / coordinate[2]
        ]

    def _convert_table_image_points_to_world_coordinates(self, table):
        image_corners = np.round(table._rectangle.as_contour_points()).astype('int')
        table_corners = [self._camera_model.compute_image_to_world_coordinates(corner[0], corner[1], 0) for corner in
                         image_corners.tolist()]
        return self._to_coordinates(table_corners)

    def _to_coordinates(self, points):
        return [Coordinate(point[0], point[1]) for point in points]

    def _get_table_dimension(self, table_corners):
        sides = self._get_table_sides_length(table_corners)
        return {
            "length": sides[0],
            "width": sides[3]
        }

    def _get_table_sides_length(self, table_corners):
        return sorted([table_corners[0].distance_from(table_corners[1]) * 4.4,
                       table_corners[1].distance_from(table_corners[2]) * 4.4,
                       table_corners[2].distance_from(table_corners[3]) * 4.4,
                       table_corners[3].distance_from(table_corners[0]) * 4.4])