#!/usr/bin/env python

"""image-view."""

from __future__ import division

import argparse
import sys

import pygame
import pygame.colordict
import pygame.font


__version__ = '0.1'


def create_window():
    """Return draw function, which takes a image filename parameter."""
    pygame.init()

    resolution = [size // 2 for size in pygame.display.list_modes()[0]]
    surface = pygame.display.set_mode(resolution)

    def draw(image_filename):
        """Draw image."""
        image_surface = pygame.image.load(image_filename)
        pygame.display.set_caption('{} {}'.format(
            image_filename,
            image_surface.get_size()))
        surface.fill(pygame.colordict.THECOLORS['white'])
        surface.blit(image_surface, (0, 0))

        pygame.display.flip()

    return draw


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(prog='image-view')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('files', nargs='+',
                        help='paths to images')
    args = parser.parse_args()

    filename_stack = list(reversed(args.files))

    try:
        draw = create_window()
        draw(filename_stack.pop())

        while True:
            event = pygame.event.wait()

            if event.type == pygame.QUIT:
                break
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                    break
            elif event.type == pygame.KEYDOWN:
                if not filename_stack:
                    break
                draw(filename_stack.pop())
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    sys.exit(main())
