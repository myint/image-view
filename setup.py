#!/usr/bin/env python
"""Setup for image-view."""

import ast

from setuptools import setup


def version():
    """Return version string."""
    with open('image_view.py') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


with open('README.rst') as readme:
    setup(name='image-view',
          version=version(),
          description='Displays Netpbm images conveniently on OS X from the '
                      'terminal.',
          long_description=readme.read(),
          license='Expat License',
          author='Steven Myint',
          url='https://github.com/myint/image-view',
          classifiers=[
              'Environment :: Console',
              'License :: OSI Approved :: MIT License',
              'Programming Language :: Python :: 2.7',
              'Programming Language :: Python :: 3',
              'Programming Language :: Python :: 3.2',
              'Programming Language :: Python :: 3.3',
              'Programming Language :: Python :: 3.4'],
          keywords='netpbm, pbm, pgm, pnm',
          py_modules=['image_view'],
          zip_safe=False,
          entry_points={
              'console_scripts': ['image-view = image_view:main']})
