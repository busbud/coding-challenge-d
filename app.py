# -*- coding: utf-8 -*-

"""
Main script for image manipulation for Busbud
"""

import multiprocessing as mp
import os

from coding_challenge_backend_d import BusbudBanner, BusbudProcess


def images():
    image_dir = os.walk('./images').next()
    for filename in image_dir[2]:
        yield open(os.path.join(image_dir[0], filename), 'rb')


def main(args):
    """
    Main script called by the command line script and eventually the
    unittest
    """
    name, image = args
    name, ext = os.path.splitext(name)

    name, content = BusbudBanner.scale_x(*BusbudBanner.load(name, image))

    p1 = BusbudProcess(ext, name, content, BusbudBanner.crop_top)
    p1.start()

    p2 = BusbudProcess(ext, name, content, BusbudBanner.crop_bottom)
    p2.start()

    # the 3rd process is ran in the current process cause it would be
    # waste not using it
    p3 = BusbudProcess(ext, name, content, BusbudBanner.crop_vmiddle)
    p3.run()

    p1.join()
    p2.join()


def script():
    """
    script called by the command line which deal with all the different images
    """
    processes = []
    for image in images():
        name = os.path.basename(image.name)
        p = mp.Process(target=main, args=((name, image,),))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()


if __name__ == '__main__':
    script()
