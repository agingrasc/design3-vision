import base64
import cv2
import numpy as np
import requests
from PIL import Image
from io import BytesIO

from infrastructure.imagesource.imagesource import ImageSource


class HTTPImageSource(ImageSource):
    def __init__(self, source_url):
        self._source_url = source_url

    def has_next_image(self):
        return True

    def next_image(self):
        data = requests.post(url=self._source_url).json()
        image = base64.b64decode(data['image'])
        img = Image.open(BytesIO(image)).convert('RGB')
        image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return image