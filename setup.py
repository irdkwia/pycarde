__version__ = '0.8.6'
import os

from setuptools import setup, find_packages

setup(
  name = 'pycarde', 
  packages = find_packages(),
  version = __version__,
  license='GPL',
  description = 'Nintendo e-Reader card-e extractor/maker.',
  author = 'irdkwia idkmn', 
  author_email = 'irdkwia2000@gmail.com', 
  url = 'https://github.com/irdkwia/pycarde/',
  keywords = ['Nintendo e-Reader', 'card-e'],
  install_requires=[
      'pillow >= 6.1.0',
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)', 
    'Programming Language :: Python :: 3', 
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
  ],
  include_package_data=True,
  package_data={
    "pycarde.data": ["*.dat", "*.png"],
    "pycarde.compression.data": ["*.dat", "*.png"],
  }
)
