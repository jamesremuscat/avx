from setuptools import setup, find_packages
import re

VERSIONFILE = "src/avx/_version.py"
verstr = "unknown"
try:
    verstrline = open(VERSIONFILE, "rt").read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
except EnvironmentError:
    print "unable to find version in %s" % (VERSIONFILE,)
    raise RuntimeError("if %s exists, it is required to be well-formed" % (VERSIONFILE,))

setup(
    name='avx',
    version=verstr,
    description='Library for controlling A/V devices',
    author='James Muscat',
    author_email='jamesremuscat@gmail.com',
    url='https://github.com/jamesremuscat/avx',
    packages=find_packages('src', exclude=["*.tests"]),
    package_dir = {'':'src'},
      long_description="""\
      AVX is a library for controlling A/V devices such as video switchers. ...
      """,
    setup_requires=["nose>=1.0"],
    tests_require=["mock"],
    install_requires=["enum34", "Pyro4>=4.20,!=4.45", "pyserial", "pyusb", "semantic_version"],
    entry_points={
        'console_scripts': [
            'avx-controller = avx.controller.Controller:main',
            ],
        }
      )
