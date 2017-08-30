from setuptools import setup
import os

requirements = ['pyvisa', 'numpy']

short_description = 'PyVisaInstrument provides boilerplate for various NI-VISA instruments.'
long_description = ('PyVisaInstrument provides boilerplate for various NI-VISA instruments.'
                    '...')

setup(name='PyVisaInstrument',
      version='0.8.0',
      description=short_description,
      long_description=long_description,
      maintainer='Adam Page',
      maintainer_email='adam.page@samtec.com',
      url='ssh://git@bitbucket.org/samteccmd/pyvisainstruments.git',
      packages=['pyvisainstrument',
                'pyvisainstrument.testsuite'],
      license='MIT',
      install_requires=requirements,
      package_data={'': ['README.rst']},
      extras_require={'libev': ['pyev']},
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Communications',
          'Topic :: Internet',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Networking'],
      platforms="Mac, Linux, Windows",
      zip_safe=True)
