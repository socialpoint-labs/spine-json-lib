#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['deepdiff>=4.0.9']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Jesus Diaz Gomez",
    author_email='yisus.gamedev@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Library to parse and edit spine animations from command line",
    entry_points={
        'console_scripts': [
            'spine_json_lib=spine_json_lib.cli:main',
        ],
    },
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=4.6.5',
            'flake8>=3.7.8',
            'tox>=3.14.0',
            'coverage>=4.5.4',
            'Sphinx>=1.8.5',
            'twine>=1.14.0'
        ]
    },
    license="MIT license",
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='spine_json_lib',
    name='spine_json_lib',
    packages=find_packages(include=['spine_json_lib', 'spine_json_lib.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/socialpoint-labs/spine_json_lib',
    version='0.0.3',
    zip_safe=False,
)
