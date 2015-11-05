from setuptools import setup, find_packages

from bluesky import __version__

test_requirements = []
with open('requirements-test.txt') as f:
    test_requirements = [r for r in f.read().splitlines()]

setup(
    name='bluesky',
    version=__version__,
    author='Joel Dubowy',
    author_email='jdubowy@gmail.com',
    packages=find_packages(),
    scripts=[
        'bin/bsp-web'
    ],
    package_data={
        'hysplit': ['bdyfiles/*.']
    },
    url='https://github.com/pnwairfire/bluesky',
    description='Tornado web app wrapping BlueSky pipeline.',
    install_requires=[
        "pyairfire>=0.8.21",
        "tornado==4.2.1"
    ],
    dependency_links=[
        "https://pypi.smoke.airfire.org/simple/pyairfire/"
    ],
    tests_require=test_requirements
)
