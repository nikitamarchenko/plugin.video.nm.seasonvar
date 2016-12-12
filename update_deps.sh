#!/usr/bin/env bash

mkdir .deps
cd .deps
wget -O kodiswift.zip https://github.com/Sinap/kodiswift/archive/0.0.7.zip
unzip kodiswift.zip
rm -rf ./../plugin.video.nm.seasonvar/resources/lib/kodiswift
mv kodiswift-0.0.7/kodiswift/ ./../plugin.video.nm.seasonvar/resources/lib/kodiswift
cd -
rm -rf .deps
