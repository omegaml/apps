#!/bin/bash
# This builds a local package repository for the packages specified in setup.py
# in general, the target platform should be the same as the platform of the pod image
# -- not all packages are built for all platforms
# -- on linux, the latest platform supported on your platform is given by ldd --version
# -- however most packages are built for either manylinux1_x86_64, or manylinux_2_17_x86_64
# -- cibuildwheel, the wheel builder used by popular open source projects, seems to select manylinux_2_17_x86_64
# -- see https://github.com/pypa/manylinux
# --     https://peps.python.org/pep-0600/
# --     https://github.com/pypa/cibuildwheel
target_platform=manylinux_2_17_x86_64
packages_dir=./packages
platform_pattern="*-cp*-*"
mkdir -p $packages_dir
#rm -f $packages_dir/*
pip download --prefer-binary -d $packages_dir .
platform_specifics=$(find $packages_dir -type f -name $platform_pattern -exec basename {} \; | cut -d- -f1 | xargs)
if [[ $platform_specifics ]]; then
  echo "Found platform specific packages: $platform_specifics. Downloading for $target_platform"
  find $packages_dir -type f -name $platform_pattern -exec rm {} \;
  pip download --no-deps --only-binary=:all: --platform $target_platform -d $packages_dir $platform_specifics
fi
echo "# created by make-localpkgs.sh $(date)" > local-requirements.txt
ls -1 $packages_dir >> local-requirements.txt
