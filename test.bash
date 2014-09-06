#!/bin/bash -eux

trap "echo -e '\x1b[01;31mFailed\x1b[0m'" ERR

python -m doctest image_view.py

./image_view.py test/*

echo -e '\x1b[01;32mOkay\x1b[0m'
