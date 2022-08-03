from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

setup_requirements = []

test_requirements = [
    "black>=22.3.0",
    "flake8>=4.0.0",
    "codecov>=2.1.4",
    "pytest>=6.2.5",
    "pytest-cov>=3.0.0",
    "pytest-html>=3.1.1",
]

dev_requirements = [
    *setup_requirements,
    *test_requirements,
    "tox>=3.24.5",
    "Sphinx==4.2.0",
]

requirements = [
    "pint==0.19.2",
    "networkx==2.8.5"
]

extra_requirements = {
    "setup": setup_requirements,
    "test": test_requirements,
    "dev": dev_requirements,
    "all": [
        *requirements,
        *dev_requirements,
    ],
}

setup(
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    name="wwtp-configuration",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    python_requires=">=3.8",
    install_requires=requirements,
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    extras_require=extra_requirements,
    test_suite="tests",
    url="https://github.com/we3lab/wwtp-configuration",
    version="0.0.1",
)
