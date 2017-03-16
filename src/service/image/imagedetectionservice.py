import cv2
import numpy as np

from math import acos

from src.detector.worldelement.iworldelementdetector import IWorldElementDetector
from src.geometry.coordinate import Coordinate
from src.world.table import Table
from src.world.world import World
from world.robot import Robot


class ImageToWorldTranslator:
    def __init__(self, camera_model):
        self._camera_model = camera_model

    def create_world(self, table):
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

    def adjust_robot_position(self, robot):
        world_position = self._camera_model.compute_image_to_world_coordinates(robot._position[0],
                                                                               robot._position[1], 5.1)
        robot.set_world_position(world_position)

        adjusted_position = self._camera_model.compute_world_to_image_coordinates(world_position[0],
                                                                                  world_position[1], 0)
        robot.set_position(adjusted_position)
        return robot

    def _convert_table_image_points_to_world_coordinates(self, table):
        table_corners = [self._camera_model.compute_image_to_world_coordinates(corner[0], corner[1], 0)
                         for corner in np.round(table._rectangle.as_contour_points()).astype('int').tolist()]
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


class ImageDetectionService:
    def __init__(self, image_to_world_translator):
        self._detectors = []
        self._image_to_world_translator = image_to_world_translator

    def translate_image_to_world(self, image):
        world = None
        robot = None
        world_elements = self.detect_all_world_elements(image)
        for element in world_elements:
            element.draw_in(image)

        for image_element in world_elements:
            if isinstance(image_element, Table):
                world = self._image_to_world_translator.create_world(image_element)
            elif isinstance(image_element, Robot):
                robot = self._image_to_world_translator.adjust_robot_position(image_element)
                cv2.circle(image, tuple(robot._position), 2, (255, 0, 0), 2)

        if robot and world is not None:
            robot.set_world_position(self.convert_target_to_world(world, robot))
        return world, robot

    def detect_all_world_elements(self, image):
        world_elements = []

        for detector in self._detectors:
            try:
                world_element = detector.detect(image)
                world_elements.append(world_element)
            except Exception as e:
                pass
                print("World initialisation failure: {}".format(type(e).__name__))

        return world_elements

    def register_detector(self, detector):
        if isinstance(detector, IWorldElementDetector):
            self._detectors.append(detector)

    def draw_world_elements_into(self, image, world_elements):
        for element in world_elements:
            element.draw_in(image)

    def convert_target_to_world(self, world, robot):
        robot_target_position = np.array([
            robot._world_position[0],
            robot._world_position[1],
            1
        ])
        return self.homogeneous_to_cart(np.dot(world._target_to_world, robot_target_position))

    def homogeneous_to_cart(self, coordinate):
        return [
            coordinate[0] / coordinate[2],
            coordinate[1] / coordinate[2]
        ]
