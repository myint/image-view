==========
image-view
==========

.. image:: https://travis-ci.org/myint/image-view.png?branch=master
    :target: https://travis-ci.org/myint/image-view
    :alt: Build status

``image-view`` displays images (PNM, PNG, JPEG, etc.) using ``pygame``.

The primary motivation is to support viewing PNM images on OS X. For common
image types, Preview works great. For PNM images, Xee_ works fine for the
most part, but it doesn't work properly when displaying a subset of images from
command line. This is important if there are a series of images captured from a
camera (``captured-00*.pgm``), and you want to display a subset of them.

.. _Xee: https://code.google.com/p/xee/


Installation
============

First install the ``pygame`` dependency somehow. One option is to use this
fork, which avoids X11 on OS X::

    $ pip install --upgrade git+https://github.com/myint/pygame

Then install the actual program::

    $ pip install --upgrade image-view


Usage
=====

Typical usage::

    $ image-view captured-070*.pgm

Use the left and right arrow keys to navigate through images.

Options::

    usage: image-view [-h] [--colorize] [--little-endian] [--version]
                      files [files ...]

    positional arguments:
      files            paths to images

    optional arguments:
      -h, --help       show this help message and exit
      --colorize       color 16-bit PGM images with a rainbow gradient
      --little-endian  interpret 16-bit PGM images as little endian; this is the
                       opposite of Netpbm (and ImageMagick)
      --version        show program's version number and exit


Example screenshot
==================

.. image:: https://raw.githubusercontent.com/myint/image-view/master/screenshot.png
    :alt: screenshot
    :align: center
