#!/usr/bin/env python

from os import path
from codecs import open
from setuptools import setup, find_packages

__version__ = '0.0.1'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

requirements = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '')
                    for x in all_reqs if x.startswith('git+')]

setup(
    version=__version__,
    install_requires=requirements,
    py_modules=['demol.cli', 'demol.utils', 'demol.definitions',
                'demol.generator'],
    packages=find_packages(),
    dependency_links=dependency_links,
    python_requires='>=3.6'
)