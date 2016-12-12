#!/usr/bin/env bash

adb connect 10.0.0.104
./adb-sync -f plugin.video.nm.seasonvar /storage/sdcard0/Android/data/org.xbmc.kodi/files/.kodi/addons/
