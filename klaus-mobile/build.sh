#!/bin/bash

# Fix permissions
chmod +x .buildozer/android/platform/python-for-android

# Run build with debug
buildozer -v android debug 2>&1 | tee build.log

# Check for success
if [ -f bin/*.apk ]; then
    cp bin/*.apk /host-output/
    echo "Build successful!"
else
    echo "Build failed. Check build.log"
    grep -i error build.log
    exit 1
fi