#!/usr/bin/env python
# coding=utf-8

from setuptools import setup


# Get long description (used on PyPI project page)
def get_long_description():
    with open('README.md', 'r') as readme_file:
        return readme_file.read()


setup(
    name='cache-simulator',
    version='2.0.1',
    description='A processor cache simulator for the MIPS ISA',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/caleb531/cache-simulator',
    author='Caleb Evans',
    author_email='caleb@calebevans.me',
    license='MIT',
    keywords='mips processor cache simulator architecture',
    packages=['cachesimulator'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'cache-simulator=cachesimulator.__main__:main'
        ]
    }
)
