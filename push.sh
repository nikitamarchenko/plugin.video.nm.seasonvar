#!/usr/bin/env bash

adb connect 10.0.0.104

DB="getSerialList main serial_map_by_id serial_names_map"
STORAGE_PATH=/storage/sdcard0/Android/data/org.xbmc.kodi/files/.kodi/userdata/addon_data/plugin.video.nm.seasonvar/.storage/

#for db_name in ${DB}; do
#    adb shell rm ${STORAGE_PATH}${db_name}
#done

adb shell rm /sdcard/temp/plugin.video.nm.seasonvar-0.0.1.zip
adb push ./dist/plugin.video.nm.seasonvar-0.0.1.zip /sdcard/temp