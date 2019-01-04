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
    'name': 'crocker',
    'version': '0.0.1',
    'packages': ['crocker'],
    'package_dir': {'': 'src'},
    'package_data': {'crocker': ['templates/*.em']},
    'entry_points': {
        'console_scripts': [
            'crocker = crocker.cli:main',
	    ],
        'crocker.extensions': [
            'dev_helpers = crocker.extensions:DevHelpers',
            'nvidia = crocker.extensions:Nvidia',
            'pulse = crocker.extensions:PulseAudio',
            'home = crocker.extensions:HomeDir',
            'user = crocker.extensions:User',
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

