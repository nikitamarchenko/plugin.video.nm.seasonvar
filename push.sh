#!/usr/bin/env bash

adb connect 10.0.0.104
adb shell rm /sdcard/temp/plugin.video.nm.seasonvar-0.0.1.zip
adb push ./dist/plugin.video.nm.seasonvar-0.0.1.zip /sdcard/temp