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


__version__ = '0.3.2'


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


def load_pgm(filename, rgb_mapper=grayscale_gradient, big_endian=True):
    """Load PGM and return pygame.Surface.

    This is only needed for 16-bit Netpbm formats, which pygame does not
    support. Return None for non-16-bit PGMs.

    >>> pgm0 = load_pgm('test/16_bit_ascii.pgm')
    >>> pgm0.get_size()
    (24, 7)

    >>> pgm1 = load_pgm('test/16_bit_ascii_without_comments.pgm')
    >>> (pygame.image.tostring(pgm0, 'RGB') ==
    ...  pygame.image.tostring(pgm1, 'RGB'))
    True

    >>> pgm_binary = load_pgm('test/16_bit_binary.pgm')
    >>> pgm_binary.get_size()
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

        if sys.byteorder == 'little' and big_endian:
            byte_array.byteswap()
    else:
        # This cannot happen since we would have raised an exception on not
        # matching the regular expression.
        assert False

    data = bytearray(rgb_mapper(byte_array, max_value))
    return pygame.image.frombuffer(data, size, 'RGB')


class Viewer(object):

    """Return draw function, which takes a image filename parameter.

    >>> viewer = Viewer()
    >>> viewer.draw('test/16_bit_ascii.pgm')

    """

    def __init__(self, colorize=False, big_endian=True):
        pygame.display.init()
        pygame.key.set_repeat(200)

        self.__surface = None
        self.__image_surface = None
        self.__rgb_mapper = (
            rainbow_gradient if colorize else grayscale_gradient)
        self.__big_endian = big_endian

    def draw(self, image_filename):
        """Draw image."""
        if image_filename:
            self.__image_surface = load_pgm(image_filename,
                                            rgb_mapper=self.__rgb_mapper,
                                            big_endian=self.__big_endian)
            if not self.__image_surface:
                try:
                    self.__image_surface = pygame.image.load(image_filename)
                except pygame.error as exception:
                    raise SystemExit('{}: {}'.format(image_filename,
                                                     exception))

            pygame.display.set_caption(os.path.basename(image_filename))

        if self.__image_surface:
            if not self.__surface:
                self.__surface = pygame.display.set_mode(
                    (max(512, self.__image_surface.get_size()[0]),
                     max(256, self.__image_surface.get_size()[1])),
                    pygame.RESIZABLE)

        self._draw()

    def _draw(self):
        """Draw contents of window."""
        self.__surface.fill(BACKGROUND)
        if self.__image_surface:
            self.__surface.blit(self.__image_surface, (0, 0))
        pygame.display.flip()

    def resize(self, size):
        """Resize the window."""
        self.__surface = pygame.display.set_mode(size, pygame.RESIZABLE)
        self._draw()


def run_user_interface(args):
    """Launch the pygame-based image viewing interface."""
    index = 0

    viewer = Viewer(colorize=args.colorize,
                    big_endian=not args.little_endian)
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
