#!/usr/bin/env python3
# coding: utf-8

import re

from setuptools import setup, find_packages


def get_version():
    VERSIONFILE = "pzhihu/__init__.py"
    verstrline = open(VERSIONFILE, "rt").read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

version = get_version()

setup(
    name='pzhihu',
    version=version,
    url='https://github.com/maicss/pa-zhihu/',
    author='Maicss',
    author_email='maicss_ke@163.com',
    description='gang si zhi hu',
    license="MIT",
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
        'requests',
        'lxml',
        'pymongo',
    ],
)
