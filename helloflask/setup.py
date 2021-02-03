#!/usr/bin/env python
from distutils.core import setup

from setuptools import find_packages

setup(name='helloflask', version='1.0', description='simple omegaml hello world flask app',
      author='omegaml',
      author_email='info@omegaml.io',
      url='http://omegaml.io',
      include_package_data=True,
      packages=find_packages(), )
