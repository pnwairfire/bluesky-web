from setuptools import setup, find_packages

from blueskyweb import __version__

requirements = []
with open('requirements.txt') as f:
    requirements = [r for r in f.read().splitlines() if not r.startswith('-')]
test_requirements = []
with open('requirements-test.txt') as f:
    test_requirements = [r for r in f.read().splitlines()]

setup(
    name='blueskyweb',
    version=__version__,
    author='Joel Dubowy',
    author_email='jdubowy@gmail.com',
    packages=find_packages(),
    scripts=[
        'bin/bsp-web'
    ],
    url='https://bitbucket.org/fera/airfire-bluesky-web',
    description='Tornado web app wrapping bluesky (https://github.com/pnwairfire/bluesky).',
    install_requires=requirements,
    tests_require=test_requirements,
    dependency_links=[
        "https://pypi.smoke.airfire.org/simple/afscripting/",
        "https://pypi.smoke.airfire.org/simple/met/",
        "https://pypi.smoke.airfire.org/simple/afconfig/"
    ]
)
