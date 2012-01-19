#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages
import sys

setup(
        name='glbase',
        version='0.0.1',
        description='OpenGL 3.2 utility',
        long_description=open('README.rst').read(),
        classifiers=[
            'Programming Language :: Python :: 2',
            'License :: OSI Approved :: zlib/libpng License',
            'Topic :: Multimedia :: Graphics :: 3D Modeling',
            ],
        keywords=['opengl'],
        author='ousttrue',
        author_email='ousttrue@gmail.com',
        license='zlib',
        install_requires=[
            'glglue', 'pymeshio',
            ],
        packages=find_packages(),
        test_suite='nose.collector',
        tests_require=['Nose'],
        )

