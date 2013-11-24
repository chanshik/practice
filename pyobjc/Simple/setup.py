"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['simple.py']
DATA_FILES = ['SimpleXibDemo.xib']

setup(
    app=APP,
    data_files=DATA_FILES,
    setup_requires=['py2app'],
)