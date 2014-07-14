import os

try:
    import setuptools
except ImportError, e:
    "FAILED! Please install or upgrade setuptools: pip install setuptools"

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.md')).read()

requires = ['numpy',
            'scipy',
            'matplotlib',
            'profilehooks',
            'nose',
            #'npshm',
            'cython',
            'decorator',
            ]

#links = ['https://github.com/sturlamolden/sharedmem-numpy/zipball/master#egg=npshm']

try:
    import cv2
except ImportError, e:
    "FAILED! Please install OpenCV and its associated Python bindings"

setup(name='schlieren',
      version='0.0',
      description='',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          ],
      author='',
      author_email='',
      url='',
      keywords='',
      packages=find_packages(),
      scripts=['bin/schlieren-cmd.py'],
      dependency_links=[],#links,
      include_package_data=True,
      zip_safe=True,
      test_suite='nose.collector',
      install_requires=requires,
      )
