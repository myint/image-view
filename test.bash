#!/bin/bash -eux

python -m doctest image_view.py

./image_view.py test/*
