import cv2


class ImageRepository:
    def load_all_images(self, images_filename):
        return [cv2.imread(filename) for filename in images_filename]
