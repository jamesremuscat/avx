from setuptools import setup, find_packages

setup(
    name='avx',
    version='0.92',
    description='Library for controlling A/V devices',
    author='James Muscat',
    author_email='jamesremuscat@gmail.com',
    url='https://github.com/jamesremuscat/avx',
    packages=find_packages('src', exclude=["*.tests"]),
    package_dir = {'':'src'},
      long_description="""\
      AVX is a library for controlling A/V devices such as video switchers. ...
      """,

      )
