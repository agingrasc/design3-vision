import cv2


class RenderingEngine:
    def render_all_elements(self, image, world_elements):
        for element in world_elements:
            if isinstance(element, list):
                for obstacle in element:
                    obstacle.draw_in(image)
            else:
                element.draw_in(image)

    def render_robot_path(self, image, robot_positions):
        for pos in robot_positions:
            cv2.circle(image, pos, 2, (0, 0, 255), 2)

    def render_path(self, image, current_robot, path):
        if path:
            prev = tuple(current_robot)
            for coord in path:
                next = coord
                cv2.line(image, prev, next, (0, 255, 0), 3)
                prev = next