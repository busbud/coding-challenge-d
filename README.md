# Busbud Coding Challenge

## Requirements

Design an application which concurrently processes a series of images
with the following treatments:

### Scaling

Images must be scaled to 1500px on the x-axis.

### Blurring

A Gaussian blur with a radius of 6px.

### Cropping

Each scaled and blurred image must produce 3 cropped images 300px tall:
one cropped from the top, one from the bottom, and one from the center.

### Saving

The resulting images must be saved into the images folder following the type
of crop performed. So rome.jpeg would result three images:

```
rome-bottom.jpeg
rome-vmiddle.jpeg
rome-top.jpeg
```

This challenge isn't intended to be a measure of your ability to manipulate
images. The basic functions have been provided for you, and it's up to you
as to how to best use them in parallel.

### Non-functional

- Must accept a tuple whose first element is a unique name for the image,
  and a file-like object as input. An example iterator `images` is provided.
- Must be written in Python 2.7 following PEP8.
- Must process images in parallel. How you organize this is entirely up to you.
  Your solution will be benchmarked.
- Must use comments wisely. Communicate why something behaves the way it does
  rather than what. It should be clear what the code does from reading it.

### Bonus Round

Extra points will be given for:

- Utilizing all CPU cores.
- Additionally scaling along the y axis and cropping along the x.


## Getting Started

Begin by forking this repo, cloning your fork, and installing its
dependencies.

### Setting up the Virtualenv

```
$ virtualenv -p python2.7 coding-challenge-backend-d
$ source coding-challenge-backend-d/bin/activate
$ cd coding-challenge-backend-d
$ git clone git@github.com:busbud/coding-challenge-d.git src
$ cd src
$ python setup.py develop
```

### Pillow

Image manipulation should be handled with the setuptools-friendly
fork of PIL, Pillow. Documentation is available in the [references](#references) section.

## References

- [PEP8](http://legacy.python.org/dev/peps/pep-0008/)
- [PEP257](http://legacy.python.org/dev/peps/pep-0257/)
- [PEP264](http://legacy.python.org/dev/peps/pep-0263/)
- [Pillow](http://pillow.readthedocs.org/en/latest/)
