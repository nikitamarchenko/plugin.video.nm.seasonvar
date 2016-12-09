#!/usr/bin/env bash

rm -rf ./dist
mkdir ./dist
pyclean $(pwd)/plugin.video.nm.seasonvar
zip -r ./dist/plugin.video.nm.seasonvar-$(python version.py).zip plugin.video.nm.seasonvar/
