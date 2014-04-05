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


def load_pgm(filename):
    """Load PGM and return pygame.Surface.

    This is only needed for 16-bit Netpbm formats, which pygame does not
    support.

    >>> pgm0 = load_pgm('test/16_bit_ascii.pgm')
    >>> pgm0.get_size()
    (24, 7)

    >>> pgm1 = load_pgm('test/16_bit_ascii_without_comments.pgm')
    >>> (pygame.image.tostring(pgm0, 'RGB') ==
    ...  pygame.image.tostring(pgm1, 'RGB'))
    True

    >>> pgm_binary = load_pgm('test/16_bit_binary.pgm')
    >>> pgm_binary.get_size()
    (32, 16)

    """
    with open(filename, mode='rb') as input_file:
        file_contents = input_file.read()

    result = re.search(MAGIC_REGEX + 3 * NUMBER_REGEX,
                       file_contents)
    if not result:
        raise SystemExit(
            "'{}' is of of an unsupported image type".format(filename))

    magic_id = result.group(1)
    size = (int(result.group(2)), int(result.group(3)))
    max_value = int(result.group(4))
    raw_data = file_contents[result.end():]

    if magic_id == b'P2':
        byte_array = [int(value) for value in raw_data.split()]
    elif magic_id == b'P5':
        byte_array = array.array('H')
        byte_array.fromstring(raw_data)
    else:
        # This cannot happen since we would have raised an exception on not
        # matching the regular expression.
        assert False

    data = bytearray(normalize_sixteen_bit(byte_array, max_value))
    return pygame.image.frombuffer(data, size, 'RGB')


def normalize_sixteen_bit(data, max_value):
    """Return 8-bit normalized integers."""
    for value in data:
        normalized = 255 * value // max_value
        yield normalized
        yield normalized
        yield normalized


def create_window():
    """Return draw function, which takes a image filename parameter.

    >>> draw = create_window()
    >>> draw('test/16_bit_ascii.pgm')

    """
    pygame.display.init()
    pygame.key.set_repeat(200)

    surface = [None]

    def draw(surface, image_filename):
        """Draw image."""
        try:
            image_surface = pygame.image.load(image_filename)
        except pygame.error:
            image_surface = load_pgm(image_filename)

        pygame.display.set_caption(os.path.basename(image_filename))

        if not surface[0]:
            surface[0] = pygame.display.set_mode(
                (max(512, image_surface.get_size()[0]),
                 max(256, image_surface.get_size()[1])))

        surface[0].fill(BACKGROUND)
        surface[0].blit(image_surface, (0, 0))

        pygame.display.flip()

    return lambda filename: draw(surface, filename)


def run_user_interface(args):
    """Launch the pygame-based image viewing interface."""
    index = 0

    draw = create_window()
    draw(args.files[index])

    while True:
        event = pygame.event.wait()

        if event.type == pygame.QUIT:
            break
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                break
            elif event.key in [pygame.K_LEFT, pygame.K_UP,
                               pygame.K_BACKSPACE]:
                index = max(0, index - 1)
            elif event.key in [pygame.K_RIGHT, pygame.K_DOWN,
                               pygame.K_SPACE]:
                index = min(len(args.files) - 1, index + 1)

            draw(args.files[index])


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(prog='image-view')
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
