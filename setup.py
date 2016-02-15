#!/usr/bin/env python
from setuptools import setup, find_packages

try:
    with open("requirements.txt", "r") as f:
        install_requires = [x.strip() for x in f.readlines()]
except IOError:
    install_requires = []

setup(name='checkit',
      version='1.0',
      description="CheckIt is a TODO list with support for multiple users",
      author='Guillermo Carrasco',
      author_email='guille.ch.88@gmail.com',
      url='https://github.com/guillermo-carrasco/checkit',
      packages=find_packages(),
      include_package_data=True,
      keywords=['TODO'],
      zip_safe=True,
      license='MIT',
      entry_points={
        'console_scripts': [
            'checkit = checkit.server:start_app',
        ],
    },
      install_requires=install_requires
)
