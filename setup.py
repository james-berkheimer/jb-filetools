## jb-filetools/setup.py
"""Package configuration."""
from setuptools import find_packages, setup
setup(
    name="filetools",
    version="0.0.1",
    packages=find_packages(where="src/filetools"),
    package_dir={"": "src/filetools"},
    install_requires=[],
    ## Entry point for command line and function to be executed
    entry_points={
        'console_scripts': ['filetools=main:main'],
    }
)