#!/usr/bin/env python

"""image-view."""

from __future__ import absolute_import
from __future__ import division

import array
import argparse
import os
import sys

import pygame


__version__ = '0.3'


BACKGROUND = (146, 146, 146)


def load_pgm(filename):
    """Load PGM and return pygame.Surface."""
    with open(filename, mode='rb') as input_file:
        magic_id = input_file.readline().strip()

        line = b'#'
        while line.startswith(b'#'):
            line = input_file.readline().strip()

        size = [int(value) for value in line.split()]

        if magic_id == b'P5':
            max_value = int(input_file.readline().strip())

            byte_array = array.array('H')
            byte_array.fromfile(input_file, size[0] * size[1])

            data = bytes(normalize_sixteen_bit(byte_array, max_value))
        else:
            raise SystemExit(
                'For 16-bit images, only binary PGMs are currently supported')

    return pygame.image.frombuffer(data, size, 'RGB')


def normalize_sixteen_bit(data, max_value):
    """Return 8-bit normalized integers."""
    for value in data:
        normalized = 255 * value // max_value
        yield normalized
        yield normalized
        yield normalized


def create_window():
    """Return draw function, which takes a image filename parameter."""
    pygame.init()
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


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(prog='image-view')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('files', nargs='+',
                        help='paths to images')
    args = parser.parse_args()

    index = 0

    try:
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
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    sys.exit(main())
