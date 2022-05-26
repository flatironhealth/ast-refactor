import os
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requires = fh.readlines()

with open("requirements-test.txt", "r") as fh:
    test_requires = fh.readlines()


setup(
    name="ast-refactor",
    version="0.1.0",
    author="Flatiron Health Data Tooling",
    author_email="data-tooling@flatiron.com",
    url="https://github.com/flatironhealth/ast-refactor",
    packages=find_packages(exclude=("doc",)),
    include_package_data=True,
    entry_points={"console_scripts": ["ast-refactor = ast_refactor.cli:cli"]},
    description="Transform code using the power of the Python AST",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD-3-Clause",
    install_requires=requires,
    test_require=test_requires,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
