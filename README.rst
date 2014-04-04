==========
image-view
==========

The purpose is to support viewing Netpbm images on OS X. Xee_ works fine for
the most part, but it doesn't work properly when displaying a subset of images
from command line. This is important if there are a series of images captured
from camera (``captured-00*.pgm``) and you want to display some subset of them.

.. _Xee: https://code.google.com/p/xee/


Installation
============

::

    $ pip install --upgrade git+https://github.com/myint/pygame
    $ pip install --upgrade image-view


Usage
=====

::

    $ image-view captured-070*.pgm

Use the left and right arrow keys to navigate through images.
