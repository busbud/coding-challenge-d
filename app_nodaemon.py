# -*- coding: utf-8 -*-

import multiprocessing
import multiprocessing.pool
import os
from PIL import Image, ImageFilter


def images():
    image_dir = os.walk('./images').next()
    for filename in image_dir[2]:
        yield open(os.path.join(image_dir[0], filename), 'rb')


def image_paths():
    image_dir = os.walk('./images').next()
    for filename in image_dir[2]:
        yield os.path.join(image_dir[0], filename)


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


def crop_and_save(name, ext, image, crop_function):
    name, image = crop_function(name, image)
    BusbudBanner.save(os.path.join('processed_images', name + ext), image)


def main(image_info):
    # We need the file extension or PIL will freak out when saving
    ext = os.path.splitext(image_info[1].name)[1] or '.jpg'

    name, image = BusbudBanner.load(*image_info)
    _, scaled = BusbudBanner.scale_x(name, image)
    _, blurred = BusbudBanner.blur(name, scaled)

    # Spawn children for two of the cropping tasks and perform the third here
    worker_top = multiprocessing.Process(target=crop_and_save, args=(
        name, ext, blurred, BusbudBanner.crop_top))
    worker_mid = multiprocessing.Process(target=crop_and_save, args=(
        name, ext, blurred, BusbudBanner.crop_vmiddle))
    worker_top.start()
    worker_mid.start()

    crop_and_save(name, ext, blurred, BusbudBanner.crop_bottom)
    worker_top.join()
    worker_mid.join()


def process_image(path):
    file_name = os.path.basename(path)
    image_name = os.path.splitext(file_name)[0]
    main((image_name, open(path, 'rb')))


class NoDaemonProcess(multiprocessing.Process):
    """Process subclass that is forcefully unable to be daemonized."""

    @property
    def daemon(self):
        return False

    @daemon.setter
    def daemon(self, _):
        """Do nothing, multiprocessing.Pool attempts to set this to True."""


class NoDaemonPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess


def process_images():
    """Process all images in parallel.

    Like app.process_images, use a process pool for convenience. The last
    three steps of the problem (cropping and saving) are also parallelized.
    This cannot be done using multiprocessing.Pool because it daemonizes its
    children processes, and they in turn cannot have children of their own.

    Use custom Pool and Process subclasses that ensure the children are not
    daemonized.
    """
    pool = NoDaemonPool()  # use cpu_count() processes
    pool.map(process_image, image_paths())
    pool.close()
    pool.join()


if __name__ == '__main__':
    process_images()
