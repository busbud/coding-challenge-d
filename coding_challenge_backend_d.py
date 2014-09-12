# -*- coding: utf-8 -*-

"""
Image manipulation and parallel execution management
"""

import os

import multiprocessing as mp

from PIL import Image, ImageFilter

PATH = os.path.join(os.path.dirname(__file__), "processed_images")


class BusbudBanner(object):
    """Image manipulation functions for Busbud Banners."""

    @classmethod
    def load(cls, name, fp):
        """Load an image from a file pointer."""
        return (name, Image.open(fp))

    @classmethod
    def save(cls, filename, image):
        """Save an image to filename"""
        image.save(filename)

    @classmethod
    def scale_x(cls, name, image, size=1500, resample=Image.BICUBIC):
        """Scale the image along its x-axis to `size` pixels."""
        x, y = image.size
        scale = float(x) / size
        x_size = size
        y_size = int(round(y / scale))
        return name, image.resize((x_size, y_size), resample)

    @classmethod
    def blur(cls, name, image, radius=6):
        """Apply a Gaussian blur to image."""
        return name + '-blur', image.filter(ImageFilter.GaussianBlur(radius))

    @classmethod
    def crop_vertical(cls, image, y_1, y_2):
        """Crop an image along its y-axis."""
        x = image.size[0]
        return image.crop((0, y_1, x, y_2))

    @classmethod
    def crop_top(cls, name, image, height=300):
        """Crop `image` to `height` pixels from the top."""
        return name + '-top', cls.crop_vertical(image, 0, height)

    @classmethod
    def crop_bottom(cls, name, image, height=300):
        """Crop `image` to `height` pixels from the bottom."""
        y = image.size[1]
        return name + '-bottom', cls.crop_vertical(image, y - height, y)

    @classmethod
    def crop_vmiddle(cls, name, image, height=300):
        """Crop `image` to `height` pixels from the middle."""
        y = image.size[1]
        offset = (y - height) / 2
        return name + '-vmiddle', cls.crop_vertical(image, offset, y - offset)


class BusbudProcess(mp.Process):
    """ Wraper around the process responsible at handling the application of
    function transformation on image in a separated process
    """
    b = BusbudBanner  # small shortcut to the image manipulation class

    def __init__(self, ext, name, content, func):
        super(BusbudProcess, self).__init__()
        self.name = name
        self.content = content
        self.ext = ext
        self.func = func

    @classmethod
    def build_path(cls, name, ext):
        return os.path.join(PATH, "{name}{ext}".format(name=name, ext=ext))

    def run(self):
        """ Executed when the process start """
        args = self.func(self.name, self.content)
        args = self.b.blur(*args)

        self.name = args[0]
        self.content = args[1]

        path = self.build_path(self.name, self.ext)
        self.b.save(path, self.content)
