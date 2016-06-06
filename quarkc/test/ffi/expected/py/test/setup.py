# Setup file for package testlib

from setuptools import setup

setup(name="testlib",
      version="1.2.3",
      install_requires=["wheel", "quark==0.0.1"],
      setup_requires=["wheel"],
      py_modules=[],
      packages=['testlib', 't2', 'testlib_md'])
