#!/bin/sh
# Rebuild job-hunting.skill from the job-hunting/ source directory.
set -e
cd "$(dirname "$0")"
rm -f job-hunting.skill
zip -r job-hunting.skill job-hunting -x '*.DS_Store'
echo "Built job-hunting.skill:"
unzip -l job-hunting.skill
