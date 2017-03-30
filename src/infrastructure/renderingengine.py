import cv2
import numpy as np


class RenderingEngine:
    def render_all_elements(self, image, world_elements):
        for element in world_elements:
            if isinstance(element, list):
                for obstacle in element:
                    obstacle.draw_in(image)
            else:
                element.draw_in(image)

    def render_actual_trajectory(self, image, robot_positions):
        for pos in robot_positions:
            cv2.circle(image, pos, 2, (0, 0, 255), 2)

    def render_planned_path(self, image, current_robot, path):
        if len(path) > 0:
            start = (np.array(path[0])).astype('int').tolist()
            prev = tuple(start)
            for coord in path[1::]:
                next = tuple(np.array([coord[0], coord[1]]).astype('int').tolist())
                cv2.line(image, prev, next, (25, 200, 25), 2)
                prev = next

        for point in path:
            cv2.circle(image, (int(point[0]), int(point[1])), 2, (40, 200, 40), 5)
