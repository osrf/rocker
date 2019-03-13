#!/usr/bin/env python3

import os
from setuptools import setup

install_requires = [
    'empy',
    'pexpect',
]

# docker API used to be in a package called `docker-py` before the 2.0 release
docker_package = 'docker'
try:
    import docker
except ImportError:
    # Docker is not yet installed, pick library based on platform
    # Use old name if platform has pre-2.0 version
    if os.path.isfile('/etc/os-release'):
        with open('/etc/os-release') as fin:
            content = fin.read()
        if 'xenial' in content:
            docker_package = 'docker-py'
else:
    # Docker is installed, pick library based on what we found
    ver = docker.__version__.split('.')
    if int(ver[0]) < 2:
        docker_package = 'docker-py'

install_requires.append(docker_package)

kwargs = {
    'name': 'rocker',
    'version': '0.1.3',
    'packages': ['rocker'],
    'package_dir': {'': 'src'},
    'package_data': {'rocker': ['templates/*.em']},
    'entry_points': {
        'console_scripts': [
            'rocker = rocker.cli:main',
            'detect_docker_image_os = rocker.cli:detect_image_os',
	    ],
        'rocker.extensions': [
            'dev_helpers = rocker.extensions:DevHelpers',
            'nvidia = rocker.nvidia_extension:Nvidia',
            'pulse = rocker.extensions:PulseAudio',
            'home = rocker.extensions:HomeDir',
            'user = rocker.extensions:User',
            'x11 = rocker.nvidia_extension:X11',
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

