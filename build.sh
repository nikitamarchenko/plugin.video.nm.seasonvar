#!/usr/bin/env bash

mkdir ./dist
pyclean $(pwd)/plugin.video.nm.seasonvar
zip -r ./dist/plugin.video.nm.seasonvar-$(python version.py).zip plugin.video.nm.seasonvar/
