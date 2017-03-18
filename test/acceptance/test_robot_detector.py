import unittest

import cv2

from detector.worldelement.robotdetector import NoRobotMarkersFound
from detector.worldelement.robotdetector import RobotDetector


class RobotDetectorTest(unittest.TestCase):
    def setUp(self):
        self.robot_detector = RobotDetector()

    def test_given_an_image_with_robot_markers_it_returns_the_robot_position(self):
        image_with_robot_markers = cv2.imread('./fixture/clean_image_with_robot_markers.jpg')
        expected_robot_position = (510, 370)

        robot_image_position = self.robot_detector.detect(image_with_robot_markers)['robot_center']

        self.assertEqual(robot_image_position, expected_robot_position)

    def test_given_an_image_without_robot_markers_it_throws_an_error(self):
        image_without_robot_markers = cv2.imread('./fixture/clean_image_without_robot_markers.jpg')

        self.assertRaises(NoRobotMarkersFound, self.robot_detector.detect, image_without_robot_markers)
