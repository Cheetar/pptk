#!/bin/bash

# Run all selenium tests in current directory.
# Headless option makes browser window not pop up during tests.

for test in ./*.side; do
  selenium-side-runner -c "browserName=firefox moz:firefoxOptions.args=[-headless]" $test
done
