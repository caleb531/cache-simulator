#!/usr/bin/env python
# coding=utf-8

from setuptools import setup


# Get long description (used on PyPI project page)
def get_long_description():
    try:
        # Use pandoc to create reStructuredText README if possible
        import pypandoc
        return pypandoc.convert('README.md', 'rst')
    except Exception:
        return None


setup(
    name='cache-simulator',
    version='2.0.0',
    description='A processor cache simulator for the MIPS ISA',
    long_description=get_long_description(),
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
