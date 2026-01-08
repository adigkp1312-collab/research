"""
Setup script for editable package installation

Install all packages in development mode:
    pip install -e .
"""

from setuptools import setup, find_packages

setup(
    name="adiyogi-langchain",
    version="0.1.0",
    packages=find_packages(where="packages"),
    package_dir={"": "packages"},
    install_requires=[
        # Core dependencies listed in apps/server/requirements.txt
        # This setup.py enables editable installs for package imports
    ],
)
