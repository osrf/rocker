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
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License'
    ],
    'description': 'A tool to run docker containers with customized extras',
    'long_description': 'A tool to run docker containers with customized extra added like nvidia gui support overlayed.',
    'license': 'Apache License 2.0',
    'python_requires': '>=3.0',

    'install_requires': install_requires,
    'url': 'https://github.com/osrf/rocker'
}

setup(**kwargs)

