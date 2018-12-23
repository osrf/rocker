#!/usr/bin/env python3

from setuptools import setup

install_requires = [
    'distro',
    'docker',
    'empy',
    'pexpect',
    'requests',
]

kwargs = {
    'name': 'rocker',
    'version': '0.0.1',
    'packages': ['rocker'],
    'package_dir': {'': 'src'},
    'package_data': {'rocker': ['templates/*.em']},
    'entry_points': {
        'console_scripts': [
            'rocker = rocker.cli:main',
	    ],
        'rocker.extensions': [
            'dev_helpers = rocker.extensions:DevHelpers',
            'nvidia = rocker.extensions:Nvidia',
            'pulse = rocker.extensions:PulseAudio',
            'home = rocker.extensions:HomeDir',
            'user = rocker.extensions:User',
        ]
	},
    'author': 'Tully Foote',
    'author_email': 'tfoote@osrfoundation.org',
    'keywords': ['Docker'],
    'classifiers': [
        'Programming Language :: Python',
        'License :: OSI Approved :: Apache Software License'
    ],
    'description': 'A tool to run docker containers with extras',
    'long_description': 'A tool to run docker containers with extra added like nvidia gui support overlayed.',
    'license': 'Apache',
    'install_requires': install_requires,
}

setup(**kwargs)

