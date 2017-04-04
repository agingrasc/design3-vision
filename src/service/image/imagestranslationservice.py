from math import acos

import numpy as np
from numpy import rad2deg
from numpy import array
from numpy import dot

import config
from domain.geometry.coordinate import Coordinate
from domain.geometry.transformationmatrixbuilder import TransformationMatrixBuilder
from domain.world.drawingarea import DrawingArea
from domain.world.robot import Robot
from domain.world.table import Table
from domain.world.world import World
from service.image.worldstate import WorldState


class ImageToWorldTranslator:
    def __init__(self, camera_model):
        self._camera_model = camera_model
        self._world = None
        self._robot = None
        self._obstacles = None
        self._drawing_area = None

    def translate_image_elements_to_world(self, image_elements):
        for image_element in image_elements:
            if isinstance(image_element, Table):
                self._world = self._translate_table_element_to_world(image_element)

            elif isinstance(image_element, DrawingArea):
                inner_square_dimension = self._get_rectangle_dimension(image_element._inner_square)
                image_element.set_inner_square_dimension(inner_square_dimension)

                top_right = image_element._outer_square.as_contour_points()[1]

                self._drawing_area = image_element

                target_point = self._camera_model.image_to_target_coordinates(top_right[0], top_right[1], 0)

                if self._world is not None:
                    world_point = self._camera_model.transform_coordinates(self._world._target_to_world,
                                                                           np.array(target_point))

                    self._drawing_area._top_right = world_point

            elif isinstance(image_element, Robot):
                self._robot = self._compute_and_set_projected_coordinates(image_element)

            elif isinstance(image_element, list):
                self._obstacles = [self._adjust_obstacle_position(obstacle) for obstacle in image_element]

        if self._robot and self._world is not None:
            robot_target_to_world_in_mm = self._target_to_world_coordinate(self._world._target_to_world,
                                                                           self._robot._world_position)
            self._robot.set_world_position(robot_target_to_world_in_mm)

        if self._obstacles and self._world is not None:
            world_obstacles = []

            for obstacle in self._obstacles:
                obstacle_target_to_world_in_mm = self._target_to_world_coordinate(self._world._target_to_world,
                                                                                  obstacle._world_position)
                obstacle.set_world_position(obstacle_target_to_world_in_mm)
                world_obstacles.append(obstacle)

            self._obstacles = world_obstacles

        return WorldState(self._world, self._robot, image_elements)

    def transform_segments(self, segmented_image, segments, scaling_factor, orientation):
        segmented_image_width = segmented_image.shape[0]
        drawing_area = self._drawing_area

        drawing_area_center = array(drawing_area._inner_square._center)
        drawing_area_inner = drawing_area._inner_square.as_coordinates()

        drawing_area_inner_width = drawing_area_inner[1].distance_from(drawing_area_inner[0])
        scaling = drawing_area_inner_width / segmented_image_width * scaling_factor

        segmented_image_center = array([segmented_image_width / 2 * scaling, segmented_image_width / 2 * scaling])
        translation = (drawing_area_center - segmented_image_center).tolist()

        scale_matrix = TransformationMatrixBuilder() \
            .scale(scaling) \
            .translate(-segmented_image_center[0], -segmented_image_center[1]) \
            .rotate(orientation) \
            .translate(segmented_image_center[0], segmented_image_center[1]) \
            .translate(translation[0], translation[1]) \
            .build()

        segments = list(map(lambda p: dot(scale_matrix, array([p[0], p[1], 1])), segments[:, 0].tolist()))
        segments = list(map(lambda p: p.astype('int').tolist()[0:2], segments))

        world_segments = self._image_to_target_list(segments, 0)
        world_segments = self._target_to_world_list(world_segments)

        return segments, world_segments

    def translate_path(self, world_path):
        if self._world:
            return self._world_to_image(world_path)
        else:
            return []

    def _compute_world_transform_matrix(self, table, world_origin):
        x_axis = np.array([world_origin, table._rectangle.as_contour_points().tolist()[1]])
        x_axis = [np.array(self._camera_model.image_to_target_coordinates(point[0], point[1], 0)) for point in
                  x_axis]

        v1 = x_axis[0]
        v2 = x_axis[1]

        x_axis = v2 - v1
        x_axis = x_axis[0:2]

        origin_x_axis = np.array([5, 0])

        angle_in_rad = acos(np.dot(origin_x_axis, x_axis) / (np.linalg.norm(origin_x_axis) * np.linalg.norm(x_axis)))

        v1[2] = 0.

        target_to_world_transform_matrix = TransformationMatrixBuilder() \
            .rotate(rad2deg(angle_in_rad)) \
            .translate(v1[0], v1[1]) \
            .inverse() \
            .build()

        return target_to_world_transform_matrix

    def _compute_and_set_projected_coordinates(self, robot):
        target_coordinates = self._camera_model.image_to_target_coordinates(robot._image_position[0],
                                                                            robot._image_position[1],
                                                                            config.ROBOT_HEIGHT_IN_TARGET_UNIT)
        robot.set_world_position(target_coordinates)

        adjusted_image_coordinates = self._camera_model.target_to_image_coordinates(target_coordinates[0],
                                                                                    target_coordinates[1],
                                                                                    0)
        robot.set_image_position(adjusted_image_coordinates)
        return robot

    def _adjust_obstacle_position(self, obstacle):
        target_coordinates = self._camera_model.image_to_target_coordinates(obstacle._position[0],
                                                                            obstacle._position[1],
                                                                            config.OBSTACLE_HEIGHT_IN_TARGET_UNIT)
        obstacle.set_world_position(target_coordinates)

        adjusted_position = self._camera_model.target_to_image_coordinates(target_coordinates[0],
                                                                           target_coordinates[1],
                                                                           0)
        obstacle.set_position(adjusted_position)
        return obstacle

    def _translate_table_element_to_world(self, table):
        table_dimensions = self._get_rectangle_dimension(table._rectangle)
        world_origin = table._rectangle.as_contour_points().tolist()[0]
        target_to_world = self._compute_world_transform_matrix(table, world_origin)

        return World(table_dimensions['width'], table_dimensions['length'],
                     world_origin[0], world_origin[1],
                     target_to_world)

    def _image_to_target_list(self, coordinates_list, height):
        return [self._camera_model.image_to_target_coordinates(p[0], p[1], height)[0:2] for p in
                coordinates_list]

    def _target_to_world_list(self, coordinates_list):
        return [self._target_to_world_coordinate(self._world._target_to_world, np.array(p)) for p in
                coordinates_list]

    def _target_to_world_coordinate(self, target_to_world_matrix, target_coordinates):
        world_position = self._camera_model.transform_coordinates(target_to_world_matrix, target_coordinates)

        world_position_in_mm = [
            world_position[0] * config.TARGET_SIDE_LENGTH,
            world_position[1] * config.TARGET_SIDE_LENGTH
        ]

        return world_position_in_mm

    def _get_rectangle_dimension(self, square):
        square_corners = np.round(square.as_contour_points()).astype('int').tolist()
        square_corners = self._image_to_target_list(square_corners, 0)
        square_corners = self._to_coordinates_list(square_corners)
        inner_dimension = self._get_element_dimension(square_corners)
        return inner_dimension

    def _get_element_dimension(self, corners):
        sides = self._get_four_sides_dimensions(corners)
        return {
            "length": sides[1],
            "width": sides[3]
        }

    def _get_four_sides_dimensions(self, table_corners):
        return sorted([table_corners[0].distance_from(table_corners[1]) * 4.4,
                       table_corners[1].distance_from(table_corners[2]) * 4.4,
                       table_corners[2].distance_from(table_corners[3]) * 4.4,
                       table_corners[3].distance_from(table_corners[0]) * 4.4])

    def _to_coordinates_list(self, points):
        return [Coordinate(point[0], point[1]) for point in points]

    def _world_to_image(self, world_path):
        translate_matrix = np.linalg.inv(self._world._target_to_world)

        target_path = [
            self._camera_model.transform_coordinates(translate_matrix, np.array(point) / config.TARGET_SIDE_LENGTH)
            for point in world_path]

        image_path = [self._camera_model.target_to_image_coordinates(point[0], point[1], 0) for point in
                      target_path]

        return image_path

    def get_obstacles(self):
        return self._obstacles

    def get_world(self):
        return self._world
