# -*- coding: utf-8 -*-

import multiprocessing
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
    crop_and_save(name, ext, blurred, BusbudBanner.crop_top)
    crop_and_save(name, ext, blurred, BusbudBanner.crop_vmiddle)
    crop_and_save(name, ext, blurred, BusbudBanner.crop_bottom)


def process_image(path):
    file_name = os.path.basename(path)
    image_name = os.path.splitext(file_name)[0]
    main((image_name, open(path, 'rb')))


def process_images():
    """Process all images in parallel.

    Use a multiprocessing.Pool instead of manually creating Processes because
    it provides a lot of useful tooling.

    Unlike Process, Pool needs to serialize all the parameters to store them
    in a Queue. When file objects are deserialized in the child process, their
    file descriptors no longer correspond to the actual open files. Use an
    intermediate function as the Pool.map target which accepts a file path,
    opens it then calls the main function using the signature specified in the
    challenge requirements.
    """
    pool = multiprocessing.Pool()  # use cpu_count() processes
    pool.map(process_image, image_paths())
    pool.close()
    pool.join()


if __name__ == '__main__':
    process_images()
