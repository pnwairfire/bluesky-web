from setuptools import setup, find_packages

from blueskyweb import __version__

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
    install_requires=[
        "pyairfire>=0.9.2",
        "tornado==4.2.1",
        "bluesky>=0.6.7",
        "requests>=2.7.0"
    ],
    dependency_links=[
        "https://pypi.smoke.airfire.org/simple/pyairfire/"
    ]
)
