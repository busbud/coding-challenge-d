# -*- coding: utf8 -*-

import os, multiprocessing, StringIO
import argparse, sys
from PIL import Image, ImageFilter


def images():
    image_dir = os.walk('./images').next()
    for filename in image_dir[2]:
        """we are sending this information to seperate processes, these
        cannot inherit a file descriptor directly from the main process,
        we transform the data in the files into StringIO types which are
        multiprocess-safe file-like objects"""

        yield filename, StringIO.StringIO(open(os.path.join(image_dir[0], filename), 'rb').read())


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

    """for extra points :)"""
    @classmethod
    def scale_y(cls, name, image, size=1000, resample=Image.BICUBIC):
        x, y = image.size
        scale = float(y) / size
        y_size = size
        x_size = int(round(x / scale))
        return name, image.resize((x_size, y_size), resample)

    @classmethod
    def crop_horizontal(cls, image, x_1, x_2):
        """Crop an image along its y-axis."""
        y = image.size[1]
        return image.crop((x_1, 0, x_2, y))

    @classmethod
    def crop_left(cls, name, image, width=300):
        """Crop `image` to `width` pixels from the left."""
        return name + '-left', cls.crop_horizontal(image, 0, width)

    @classmethod
    def crop_right(cls, name, image, width=300):
        """Crop `image` to `width` pixels from the right."""
        x = image.size[0]
        return name + '-right', cls.crop_horizontal(image, x - width, x)

    @classmethod
    def crop_hmiddle(cls, name, image, width=300):
        """Crop `image` to `width` pixels from the middle."""
        x = image.size[0]
        offset = (x - width) / 2
        return name + '-hmiddle', cls.crop_horizontal(image, offset, x - offset)





"""helper functions to crop and save in batch

they are all set aside within these two functions as they are fast and calling
them each within a single process is not necessarily a speedup"""
def crop_and_save_x(name, im):
    name, extension = os.path.splitext(name)

    for cropper in [BusbudBanner.crop_top, BusbudBanner.crop_bottom, BusbudBanner.crop_vmiddle]:
        cropped_name, cropped = cropper(name, im)
        BusbudBanner.save(os.path.join('./processed_images/', cropped_name + extension), cropped)

    return name, im

def crop_and_save_y(name, im):
    name, extension = os.path.splitext(name)

    for cropper in [BusbudBanner.crop_left, BusbudBanner.crop_right, BusbudBanner.crop_hmiddle]:
        cropped_name, cropped = cropper(name, im)
        BusbudBanner.save(os.path.join('./processed_images/', cropped_name + extension), cropped)

    return name, im


"""threadsafe queue to pass things around"""
q = multiprocessing.Manager().Queue()

"""set of tasks to perform in order on each image
the 'reset' is simply to reset operations when applying on both x-scaled
and y-scaled axii

use one of the three following lists to perform desired operations, the parameter
is set on command line """
x_task_pool = [BusbudBanner.load, BusbudBanner.scale_x, BusbudBanner.blur, crop_and_save_x]
y_task_pool = [BusbudBanner.load, BusbudBanner.scale_y, BusbudBanner.blur, crop_and_save_y]
both_task_pool = [BusbudBanner.load, BusbudBanner.scale_x, BusbudBanner.blur, crop_and_save_x, 'reset', BusbudBanner.load, BusbudBanner.scale_y, BusbudBanner.blur, crop_and_save_y]
task_pool = []


"""this function gets the current position in the queue, applies the desired
function from task_pool and puts a new tuple at the end of queue for the
next task on file.

The idea is to be able to control the sequence of calls on each file without
waiting for other files to finish each step, everything happens in parallel"""
def next_task(num):
    Timage = q.get()

    if task_pool[Timage[2]] == 'reset':
        im = StringIO.StringIO(Timage[3].getvalue())
    else:
        name, im = task_pool[Timage[2]](Timage[0], Timage[1])

    if Timage[2]+1 < len(task_pool):
        q.put([Timage[0], im, Timage[2]+1, Timage[3]])



def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', dest='type', help='define axis scaling type by using: x for x-scaling, y for y-scaling and both to apply both scalings', default='x')
    args = parser.parse_args()

    allowed_types = {'x':x_task_pool, 'y':y_task_pool, 'both':both_task_pool}

    if args.type not in allowed_types:
        parser.print_help()
        sys.exit(1)

    global task_pool
    task_pool = allowed_types[args.type]

    """We use multiprocessing instead of threading module as this allows
    to control the number of processes and how many can run at the same
    time using the Pool class"""
    n_cpus = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(n_cpus)

    n_files = 0
    for filename, flo in images():
        n_files += 1
        q.put([filename, flo, 0, flo])

    """start pooling, using map allows us to control the number of iterations"""
    pool.map(next_task,range(n_files*len(task_pool)))


if __name__ == '__main__':
    main(sys.argv[1:])
