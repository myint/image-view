#!/usr/bin/env python

"""image-view."""

from __future__ import absolute_import
from __future__ import division

import argparse
import os
import sys

import pygame


__version__ = '0.2'


BACKGROUND = (146, 146, 146)


def create_window():
    """Return draw function, which takes a image filename parameter."""
    pygame.init()
    pygame.key.set_repeat(75)

    surface = [None]

    def draw(surface, image_filename):
        """Draw image."""
        image_surface = pygame.image.load(image_filename)

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
                elif event.key in [pygame.K_LEFT, pygame.K_UP]:
                    index = max(0, index - 1)
                elif event.key in [pygame.K_RIGHT, pygame.K_DOWN]:
                    index = min(len(args.files) - 1, index + 1)

                draw(args.files[index])
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    sys.exit(main())
