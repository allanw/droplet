#!/usr/bin/env python
import sys
from setuptools import setup

if sys.version < "2.5":
    sys.exit("Python 2.5 or higher is required")

setup(
    name="droplet",
    version="0.1",
    description="A Dropbox-based blog engine written using the Bottle web framework",
    # long_description="""""",
    license="Apache License 2.0",
    author="Al Whatmough",
    url="https://github.com/allanw/droplet",
    install_requires=[
        "bottle", "dropbox", "redis", "markdown", "pygments",
    ],
    packages=["droplet"],
    classifiers=[
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
    ],
    package_data={
        "": ["*.html"]
    },
)
