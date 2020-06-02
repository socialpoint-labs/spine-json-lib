#!/usr/bin/env python

"""The setup script."""
import io
import re

from setuptools import setup, find_packages

with io.open("spine_json_lib/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE
    ).group(1)

with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()


requirements_dev = [
    "flake8>=3.7.8",
    "tox>=3.14.0",
    "coverage>=4.5.4",
]

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest>=3",
    "deepdiff>4.0",
    "pip>=15.0.0",
]

setup(
    author="Jesus Diaz Gomez",
    author_email="yisus.gamedev@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Library to parse and edit spine animations from command line",
    entry_points={"console_scripts": ["spine_json_lib=spine_json_lib.cli:main",],},
    install_requires=[],
    extras_require={"dev": requirements_dev},
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="spine_json_lib",
    name="spine_json_lib",
    packages=find_packages(include=["spine_json_lib", "spine_json_lib.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/socialpoint-labs/spine-json-lib",
    version=version,
    zip_safe=False,
)
