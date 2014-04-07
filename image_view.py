#!/usr/bin/env python

"""Image viewer."""

from __future__ import absolute_import
from __future__ import division

import array
import argparse
import os
import re
import signal
import sys

import pygame


__version__ = '0.4.1'


BACKGROUND = (146, 146, 146)
MAGIC_REGEX = br'\s*(P[25])\s*(?:#.*[\r\n])*'
NUMBER_REGEX = br'\s*(\d+)\s*(?:#.*[\r\n])*'


def grayscale_gradient(data, max_value):
    """Return 8-bit normalized RGB integers.

    >>> list(grayscale_gradient([1], 2))
    [127, 127, 127]

    """
    for value in data:
        normalized = 255 * value // max_value
        yield normalized
        yield normalized
        yield normalized


def rainbow_gradient(data, max_value):
    """Return 8-bit normalized RGB integers.

    >>> list(rainbow_gradient([0], 2))
    [0, 0, 255]

    >>> list(rainbow_gradient([1], 2))
    [0, 255, 0]

    >>> list(rainbow_gradient([2], 2))
    [255, 0, 0]

    """
    for value in data:
        middle = max_value / 2.
        r = int(max(0, 255. * (value / middle - 1.)))
        b = int(max(0, 255. * (1. - value / middle)))
        yield r
        yield 255 - b - r
        yield b


def load_pgm(filename, rgb_mapper=grayscale_gradient, little_endian=False):
    """Load PGM and return pygame.Surface.

    This is only needed for 16-bit PGM formats, which pygame does not
    support. Return None for non-16-bit PGMs.

    >>> pgm0 = load_pgm('test/16_bit_ascii.pgm')
    >>> pgm0.get_size()
    (24, 7)

    >>> pgm1 = load_pgm('test/16_bit_ascii_without_comments.pgm')
    >>> (pygame.image.tostring(pgm0, 'RGB') ==
    ...  pygame.image.tostring(pgm1, 'RGB'))
    True

    >>> pgm_binary0 = load_pgm('test/16_bit_binary.pgm')
    >>> pgm_binary0.get_size()
    (20, 100)

    >>> load_pgm('test/8_bit_binary.pgm') is None
    True

    """
    with open(filename, mode='rb') as input_file:
        file_contents = input_file.read()

    result = re.search(MAGIC_REGEX + 3 * NUMBER_REGEX,
                       file_contents)
    if not result:
        return None

    magic_id = result.group(1)
    size = (int(result.group(2)), int(result.group(3)))
    max_value = int(result.group(4))
    raw_data = file_contents[result.end():]

    if max_value <= 255:
        return None

    if magic_id == b'P2':
        byte_array = [int(value) for value in raw_data.split()]
    elif magic_id == b'P5':
        byte_array = array.array('H')
        # Ignore any junk at the end of the file.
        byte_array.fromstring(raw_data[:2 * size[0] * size[1]])

        if sys.byteorder != ('little' if little_endian else 'big'):
            byte_array.byteswap()
    else:
        # This cannot happen since we would have raised an exception on not
        # matching the regular expression.
        assert False

    data = bytearray(rgb_mapper(byte_array, max_value))
    return pygame.image.frombuffer(data, size, 'RGB')


def load_image(filename, **kwargs):
    """Return pygame.Surface.

    This uses "load_pgm()" for 16-bit PGM images.

    >>> surface = load_image('test/python.png')
    >>> surface.get_size()
    (50, 65)

    A 16-bit binary PGM should be nearly equivalent to its 8-bit counterpart.

    >>> pgm_binary0 = load_image('test/16_bit_binary.pgm')
    >>> pgm_binary1 = load_image('test/8_bit_binary.pgm')
    >>> for j in range(pgm_binary0.get_height()):
    ...     assert abs(pgm_binary0.get_at((0, j))[0] -
    ...                pgm_binary1.get_at((0, j))[0]) <= 1

    """
    surface = load_pgm(filename, **kwargs)
    if not surface:
        try:
            surface = pygame.image.load(filename)
        except pygame.error as exception:
            raise SystemExit('{}: {}'.format(filename, exception))

    return surface


class Viewer(object):

    """Return draw function, which takes a image filename parameter.

    >>> viewer = Viewer()
    >>> viewer.draw('test/16_bit_ascii.pgm')
    >>> viewer.resize((640, 480))
    >>> viewer.scale_down()
    >>> viewer.draw('test/python.png')

    The scale is capped once pygame throws and error.

    >>> for _ in range(10):
    ...     viewer.scale_up()
    >>> viewer.draw('test/python.png')

    """

    def __init__(self, colorize=False, little_endian=False):
        pygame.display.init()
        pygame.key.set_repeat(200)

        self.__surface = None
        self.__image_surface = None
        self.__rgb_mapper = (
            rainbow_gradient if colorize else grayscale_gradient)
        self.__little_endian = little_endian
        self.__scale = 1

    def draw(self, image_filename):
        """Draw image."""
        if image_filename:
            self.__image_surface = load_image(
                image_filename,
                rgb_mapper=self.__rgb_mapper,
                little_endian=self.__little_endian)

            while self.__scale > 1:
                try:
                    self.__image_surface = _scale(self.__image_surface,
                                                  self.__scale)
                    break
                except pygame.error:
                    self.scale_down()

            pygame.display.set_caption('{}{}'.format(
                os.path.basename(image_filename),
                '' if self.__scale == 1 else ' ({}x)'.format(self.__scale)))

        if self.__image_surface:
            if not self.__surface:
                self.__surface = pygame.display.set_mode(
                    (max(512, self.__image_surface.get_size()[0]),
                     max(256, self.__image_surface.get_size()[1])),
                    pygame.RESIZABLE)

        self._draw()

    def resize(self, size):
        """Resize the window."""
        self.__surface = pygame.display.set_mode(size, pygame.RESIZABLE)
        self._draw()

    def scale_up(self):
        """Scale the image up by two."""
        self.__scale = min(1024, self.__scale * 2)

    def scale_down(self):
        """Scale the image down by two."""
        self.__scale = max(1, self.__scale // 2)

    def scale_default(self):
        """Set the image to its default scale."""
        self.__scale = 1

    def _draw(self):
        """Draw contents of window."""
        self.__surface.fill(BACKGROUND)
        if self.__image_surface:
            self.__surface.blit(self.__image_surface, (0, 0))
        pygame.display.flip()


def _scale(image_surface, scale):
    """Return scaled image."""
    actual_size = image_surface.get_size()
    return pygame.transform.scale(
        image_surface,
        (scale * actual_size[0],
         scale * actual_size[1]))


def run_user_interface(args):
    """Launch the pygame-based image viewing interface."""
    index = 0

    viewer = Viewer(colorize=args.colorize,
                    little_endian=args.little_endian)
    viewer.draw(args.files[index])

    while True:
        event = pygame.event.wait()

        if event.type == pygame.QUIT:
            break
        elif event.type == pygame.VIDEORESIZE:
            viewer.resize(event.dict['size'])
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                break
            elif event.key in [pygame.K_LEFT, pygame.K_UP,
                               pygame.K_BACKSPACE]:
                index = max(0, index - 1)
            elif event.key in [pygame.K_RIGHT, pygame.K_DOWN,
                               pygame.K_SPACE]:
                index = min(len(args.files) - 1, index + 1)
            elif event.unicode:
                # Make sure "event.unicode" is not the empty string.
                if event.unicode in '+=':
                    viewer.scale_up()
                elif event.unicode in '-_':
                    viewer.scale_down()
                elif event.unicode in '0':
                    viewer.scale_default()

            viewer.draw(args.files[index])


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(prog='image-view')
    parser.add_argument('--colorize', action='store_true',
                        help='color 16-bit PGM images with a rainbow gradient')
    parser.add_argument('--little-endian', action='store_true',
                        help='interpret 16-bit PGM images as little endian; '
                             'this is the opposite of Netpbm '
                             '(and ImageMagick)')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('files', nargs='+',
                        help='paths to images')
    args = parser.parse_args()

    # This is necessary because somehow pygame (at least on OS X) interferes
    # with the raising of KeyboardInterrupt.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    run_user_interface(args)


if __name__ == '__main__':
    sys.exit(main())
