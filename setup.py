from setuptools import setup
import io
import re

with open('README.md', 'r') as fp:
    long_description = fp.read()

with io.open("pyvisainstrument/__init__.py", "rt", encoding="utf8") as fp:
    version = re.search(r'__version__ = "(.*?)"', fp.read()).group(1)
    (major_version, minor_version, revision) = version.split('.')

requirements = ['pyvisa', 'numpy']

short_description = 'PyVisaInstrument provides boilerplate for various NI-VISA instruments.'

setup(
    name='PyVisaInstrument',
    version=version,
    description=short_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Samtec - ASH',
    author_email='samtec-ash@samtec.com',
    url='https://github.com/Samtec-ASH/pyvisainstrument',
    packages=[
        'pyvisainstrument',
        'pyvisainstrument.testsuite'
    ],
    license='MIT',
    install_requires=requirements,
    extras_require={'libev': ['pyev']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking'],
    platforms="Mac, Linux, Windows",
    zip_safe=True
)
